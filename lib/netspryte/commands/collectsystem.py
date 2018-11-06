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
import logging
import glob
import pprint
import datetime
import time
import traceback
import multiprocessing

import netspryte
import netspryte.system
from netspryte.plugins import system_module_loader

from netspryte.commands import BaseCommand
from netspryte import constants as C
from netspryte.utils import setup_logging, xlate_metric_names, get_db_backend
from netspryte.utils.timer import Timer
from netspryte.utils.worker import CollectWorker
from netspryte.manager import Manager, MeasurementInstance, MeasurementClass, Host


class CollectSystemCommand(BaseCommand):

    SYSTEM_MODULES = list()

    def __init__(self, daemonize=False):
        super(CollectSystemCommand, self).__init__(daemonize)

    def run(self):
        args = self.parser.parse_args()
        if not args.datadir or not os.path.exists(args.datadir):
            logging.error("Path to data directory does not exist: %s", args.datadir)
            return 1
        setup_logging(args.verbose)
        t = Timer("system collection")
        t.start_timer()
        cfg = C.load_config()
        num_workers = C.DEFAULT_WORKERS
        if len(args.devices) < num_workers:
            num_workers = len(args.devices)
        logging.warn("beginning system collection with %s workers", num_workers)
        CollectSystemCommand.SYSTEM_MODULES = system_module_loader.all()
        task_queue = multiprocessing.JoinableQueue()
        if args.nofork:
            num_workers = 1
        logging.info("creating %s workers", num_workers)
        workers = [CollectWorker(task_queue) for i in range(num_workers)]
        for w in workers:
            w.start()
        for d in args.devices:
            task_queue.put(d)
        # add poison pill to queue
        for i in range(num_workers):
            task_queue.put(None)
        task_queue.join()
        t.stop_timer()


class CollectSystemWorker(CollectWorker):

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
            t.name = "%s system worker" % device
            t.start_timer()
            logging.warn("processing %s", device)
            try:
                for cls, module in list(CollectSystemCommand.SYSTEM_MODULES.items()):
                    try:
                        system_mod = cls(config)
                        name = system_mod.host
                        if system_mod and hasattr(system_mod, 'data'):
                            self.process_module_data(system_mod)
                    except Exception as e:
                        logging.error("module %s failed against device %s: %s", cls.__name__, device, traceback.format_exc())
                        continue
            except Exception as e:
                logging.error("encountered error with %s; skipping to next device: %s", device, traceback.format_exc())
            finally:
                t.stop_timer()
            self.task_queue.task_done()
        return
