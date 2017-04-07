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

import netspryte
import netspryte.snmp
from netspryte.plugins import snmp_module_loader

from netspryte.commands import BaseCommand
from netspryte import constants as C
from netspryte.utils import *
from netspryte.db.manager import *
from netspryte.db.rrd import *

class CollectSnmpCommand(BaseCommand):

    SNMP_MODULES = list()

    def __init__(self, daemonize=False):
        super(CollectSnmpCommand, self).__init__(daemonize)
        self.parser.add_argument('-M', '--metrics', default=False, action='store_true',
                                 help="Collect only from SNMP modules with metrics")
        self.parser.add_argument('devices', type=str, nargs='*',
                                 default=C.DEFAULT_DEVICES,
                                 help='list of devices to query')

    def run(self):
        args = self.parser.parse_args()
        if not args.datadir or not os.path.exists(args.datadir):
            logging.error("Path to data directory does not exist: %s", args.datadir)
            return 1
        setup_logging(args.verbose)
        stime = time.time()
        logging.warn("devices are: %s", ", ".join(args.devices))
        logging.warn("beginning snmp collection")
        cfg = C.load_config()
        num_workers = C.DEFAULT_WORKERS
        if len(args.devices) < num_workers:
            num_workers = len(args.devices)
        CollectSnmpCommand.SNMP_MODULES = snmp_module_loader.all()
        task_queue = multiprocessing.JoinableQueue()
        if args.nofork:
            num_workers = 1
        logging.info("creating %s workers", num_workers)
        workers = [ CollectSnmpWorker(task_queue, args.metrics)
                    for i in range(num_workers) ]
        for w in workers:
            w.start()
        for d in args.devices:
            task_queue.put(d)
        # add poison pill to queue
        for i in range(num_workers):
            task_queue.put(None)
        task_queue.join()
        etime = time.time()
        elapsed = etime - stime
        logging.warn("snmp collection elapsed time: %.2f", elapsed)


class CollectSnmpWorker(multiprocessing.Process):

    def __init__(self, task_queue, metrics_only):
        multiprocessing.Process.__init__(self)
        self.task_queue = task_queue
        self.metrics_only = metrics_only
        self.stat = dict()

    def run(self):
        proc_name = self.name
        while True:
            device = self.task_queue.get()
            if device is None:
                logging.info("worker %s exiting", proc_name)
                self.task_queue.task_done()
                break
            self.stat['stime'] = time.time()
            logging.warn("processing %s", device)
            try:
                msnmp = netspryte.snmp.SNMPSession(host=device)
                self.stat['host'] = msnmp.host
                for cls, module in CollectSnmpCommand.SNMP_MODULES.iteritems():
                    if self.metrics_only and not cls.STAT:
                        continue
                    try:
                        snmp_mod = cls(msnmp)
                        name = snmp_mod.sysName or msnmp.host
                        if snmp_mod and hasattr(snmp_mod, 'data'):
                            self.process_module_data(snmp_mod)
                    except Exception as e:
                        logging.error("module %s failed against device %s: %s", cls.__name__, device, traceback.format_exc())
                        continue
            except Exception as e:
                logging.error("encountered error with %s; skipping to next device: %s", device, traceback.format_exc())
            finally:
                self.stat['etime'] = time.time()
                self.stat['elapsed'] = self.stat['etime'] - self.stat['stime']
                logging.warn("%s elapsed time: %.2f", device, self.stat['elapsed'])
            self.task_queue.task_done()
        return

    def process_module_data(self, snmp_mod):
        mgr = Manager()
        this_class_updated = False
        for data in snmp_mod.data:
            now = datetime.datetime.now()
            this_host = mgr.get_or_create(Host, name=data['host'])
            this_class = mgr.get_or_create(MeasurementClass, name=data['class'], transport=data['transport'])
            if hasattr(snmp_mod, 'DESCRIPTION') and not this_class.description:
                this_class.description = snmp_mod.DESCRIPTION
            this_inst = mgr.get_or_create(MeasurementInstance,
                                          name=data['name'], index=data['index'],
                                          host=this_host, measurement_class=this_class)
            this_host.lastseen = now
            this_inst.lastseen = now
            this_inst.attrs = json_ready(data['attrs'])
            if 'presentation' in data and not this_inst.presentation:
                this_inst.presentation = json_ready(data['presentation'])
            if 'metrics' in data:
                this_inst.metrics = json_ready(data['metrics'])
            # attrs = data['attrs']
            if 'metrics' in data:
                metric_types = dict()
                for k, v in data['metrics'].iteritems():
                    metric_types[k] = netspryte.snmp.get_value_type(v)
                this_class.metric_type = json_ready(metric_types)
                metrics = CollectSnmpWorker.xlate_data(data['metrics'], snmp_mod.XLATE)
                self.process_data_instance(snmp_mod, snmp_mod.NAME, data, metrics)
            mgr.save(this_inst)
            if not this_class_updated:
                mgr.save(this_host)
                mgr.save(this_class)
                this_class_updated = True

    def process_data_instance(self, mod, name, data, values):
        ''' '''
        if not values:
            return
        rrd_path = mk_rrd_filename(mod, name, data['index'])
        dbs = get_db_backend()
        for db in dbs:
            if db.backend == 'rrd':
                db.path = rrd_path
            self.record_stats(db, values)

    @staticmethod
    def record_stats(db, data):
        db.write(data)

    @staticmethod
    def xlate_data(data, xlate):
        values = dict()
        for k in data:
            newk = CollectSnmpWorker.clean_name(k, xlate)
            values[newk] = data[k]
        return values

    @staticmethod
    def clean_name(name, xlate):
        for k,v in xlate.iteritems():
            name = name.replace(k, v, 1)
        return name

