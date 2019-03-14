# Written by Stephen Fromm <stephenf nero net>
# Copyright Copyright (C) 2015-2017 University of Oregon
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.

import argparse
import os
import sys
import logging
import glob
import pprint
import datetime
import time
import traceback
import multiprocessing
import random
from peewee import BigIntegerField, DecimalField

import netspryte
import netspryte.snmp
from netspryte.plugins import snmp_module_loader

from netspryte.commands import BaseCommand
from netspryte import constants as C
from netspryte.utils import setup_logging, json_ready, xlate_metric_names, get_db_backend
from netspryte.utils.timer import Timer
from netspryte.utils.worker import DataWorker
from netspryte.manager import Manager
from netspryte.db.rrd import *


class CollectSnmpCommand(BaseCommand):

    SNMP_MODULES = list()

    def __init__(self, daemonize=False):
        super(CollectSnmpCommand, self).__init__(daemonize)
        self.parser.add_argument('devices', type=str, nargs='*',
                                 default=C.DEFAULT_DEVICES,
                                 help='list of devices to query')

    def run(self):
        args = self.parser.parse_args()
        if not args.datadir or not os.path.exists(args.datadir):
            logging.error("Path to data directory does not exist: %s", args.datadir)
            return 1
        setup_logging(args.verbose)
        t = Timer("snmp collection")
        t.start_timer()
        cfg = C.load_config()
        num_workers = C.DEFAULT_WORKERS
        if len(args.devices) < num_workers:
            num_workers = len(args.devices)
        logging.warn("beginning snmp collection with %s workers", num_workers)
        CollectSnmpCommand.SNMP_MODULES = snmp_module_loader.all()
        task_queue = multiprocessing.JoinableQueue()
        if args.nofork:
            num_workers = 1
        logging.info("creating %s workers", num_workers)
        workers = [CollectSnmpWorker(task_queue) for i in range(num_workers)]
        for w in workers:
            w.start()
        for d in args.devices:
            task_queue.put(d)
        # add poison pill to queue
        for i in range(num_workers):
            task_queue.put(None)
        task_queue.join()
        t.stop_timer()


class CollectSnmpWorker(DataWorker):

    def run(self):
        self.mgr = Manager()
        proc_name = self.name
        t = Timer()
        while True:
            device = self.task_queue.get()
            if device is None:
                logging.info("worker %s exiting", proc_name)
                self.task_queue.task_done()
                break
            t.name = "%s snmp worker" % device
            t.start_timer()
            logging.warn("processing %s", device)
            try:
                msnmp = netspryte.snmp.SNMPSession(host=device)
                for cls, module in list(CollectSnmpCommand.SNMP_MODULES.items()):
                    if not cls.STAT:
                        logging.info("skipping module %s that does not collect measurement data", cls.NAME)
                        continue
                    try:
                        snmp_mod = cls(msnmp)
                        hostname = snmp_mod.sysName or msnmp.host
                        if snmp_mod and hasattr(snmp_mod, 'data'):
                            has_metrics = self.process_module_data(snmp_mod)
                            self.process_metrics(has_metrics, snmp_mod, hostname)
                    except Exception as e:
                        logging.error("module %s failed against device %s: %s", cls.__name__, device, traceback.format_exc())
                        continue
            except Exception as e:
                logging.error("encountered error with %s; skipping to next device: %s", device, traceback.format_exc())
            finally:
                t.stop_timer()
            self.task_queue.task_done()
        return

    def process_metrics(self, measurement_instances, snmp_mod, hostname):
        ''' Take list of instances and process the metrics '''
        if not measurement_instances:
            logging.info("%s no metrics to record for module %s", hostname, snmp_mod.NAME)
            return
        # reset hostname to what is recorded in the measurement instance
        hostname = measurement_instances[0].host.name
        measurement_class = measurement_instances[0].measurement_class.name
        t = Timer("%s-%s-metrics update" % (hostname, measurement_class))
        t.start_timer()
        for this_inst in measurement_instances:
            self.process_measurement_instance_metrics(this_inst, snmp_mod.XLATE)
        t.stop_timer()

    def process_measurement_instance_metrics(self, measurement_instance, xlate):
        ''' process a single instance data '''
        # querying <class>_metrics returns a ModelSelect, not the results from a query.
        # Will want to carefully consider how to limit to most recent timestamp
        m = getattr(measurement_instance, "%s_metrics" % (measurement_instance.measurement_class.name)).limit(1).get()
        data = self.mgr.to_dict(m)
        # Clean up the dictionary data and remove non-metric columns
        for field in m.__class__._meta.sorted_fields:
            if not isinstance(field, BigIntegerField) and not isinstance(field, DecimalField):
                del(data[field.name])
        metrics = xlate_metric_names(data, xlate)
        dbs = get_db_backend()
        for db in dbs:
            db.measurement_instance = measurement_instance
            db.write(metrics, xlate)
