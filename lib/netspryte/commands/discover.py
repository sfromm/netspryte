# Written by Stephen Fromm <stephenf nero net>
# Copyright (C) 2015-2017 University of Oregon
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
import datetime
import os
import sys
import logging
import glob
import traceback
import multiprocessing

import netspryte
import netspryte.snmp
from netspryte.plugins import snmp_module_loader

from netspryte.commands import BaseCommand
from netspryte import constants as C
from netspryte.utils import setup_logging, json_ready
from netspryte.utils.timer import Timer
from netspryte.utils.worker import DataWorker
from netspryte.manager import Manager, MeasurementInstance, MeasurementClass, Host


class DiscoverCommand(BaseCommand):

    def __init__(self, daemonize=False):
        super(DiscoverCommand, self).__init__(daemonize)
        self.parser.add_argument('devices', type=str, nargs='*',
                                 default=C.DEFAULT_DEVICES,
                                 help='list of devices to query')

    def run(self):
        args = self.parser.parse_args()
        setup_logging(args.verbose)
        t = Timer("discover")
        t.start_timer()
        cfg = C.load_config()
        num_workers = C.DEFAULT_WORKERS
        if len(args.devices) < num_workers:
            num_workers = len(args.devices)
        logging.warn("beginning discover with %s workers", num_workers)
        DiscoverCommand.SNMP_MODULES = snmp_module_loader.all()
        task_queue = multiprocessing.JoinableQueue()
        if args.nofork:
            num_workers = 1
        logging.info("creating %s workers", num_workers)
        workers = [DiscoverWorker(task_queue) for i in range(num_workers)]
        for w in workers:
            w.start()
        for d in args.devices:
            task_queue.put(d)
        # add poison pill to queue
        for i in range(num_workers):
            task_queue.put(None)
        task_queue.join()
        t.stop_timer()


class DiscoverWorker(DataWorker):

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
            t.name = "%s discover worker" % device
            t.start_timer()
            logging.warn("processing %s", device)
            try:
                msnmp = netspryte.snmp.SNMPSession(host=device)
                for cls, module in list(DiscoverCommand.SNMP_MODULES.items()):
                    try:
                        snmp_mod = cls(msnmp)
                        modname = cls.__name__
                        if snmp_mod and hasattr(snmp_mod, 'data'):
                            self.process_module_data(snmp_mod)
                    except Exception as e:
                        logging.error("module %s failed against device %s: %s", modname, device, traceback.format_exc())
                        continue
            except Exception as e:
                logging.error("encountered error with %s; skipping to next device: %s", device, traceback.format_exc())
            finally:
                t.stop_timer()
            self.task_queue.task_done()
        self.mgr.close()
        return
