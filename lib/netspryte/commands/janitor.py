# Written by Stephen Fromm <stephenf nero net>
# Copyright (C) 2017 University of Oregon
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
import re
import crontab

import netspryte
from netspryte.manager import *

from netspryte.commands import BaseCommand
from netspryte import constants as C
from netspryte.utils import *

class JanitorCommand(BaseCommand):

    def __init__(self, daemonize=False):
        super(JanitorCommand, self).__init__(daemonize)
        group1 = self.parser.add_argument_group('tag', 'Tag measurement instances')
        group1.add_argument('-i', '--instance', action='append',
                            help='measurement instance to tag')
        group1.add_argument('-t', '--tag', action='append',
                            help='tag name')
        group2 = self.parser.add_argument_group('cron', 'Crontab commands')
        group2.add_argument('-a', '--action', choices=['add', 'delete', 'show'],
                            help='Add, delete, or show a crontab')
        group2.add_argument('-j', '--cron',
                            help='Cron job to add/remove')
        group2.add_argument('-I', '--interval',
                            help='Time interval to run cron job')
        self.parser.add_argument('command', type=str,
                                 choices=['tag', 'cron'],
                                 help="Sub-command")

    def run(self):
        args = self.parser.parse_args()
        setup_logging(args.verbose)
        self.mgr = Manager()
        if args.command == 'tag':
            self.tag_command(args.tag, args.instance)
        elif args.command == 'cron':
            self.crontab_command(args.action, args.cron, args.interval)
        else:
            logging.error("unrecognized command")

    def tag_command(self, tags, instances):
        ''' tag measurement instances '''
        if not tags or not instances:
            logging.error("no tags or measurement instances provided")
            return
        for tag in tags:
            this_tag = self.mgr.get_or_create(Tag, name=tag)
            for inst in instances:
                this_inst = self.mgr.get(MeasurementInstance, name=inst)
                if not this_inst:
                    continue
                logging.warn("tagging measurement instance %s with tag %s", this_inst.name, tag)
                this_inst_tag = self.mgr.get_or_create(MeasurementInstanceTag,
                                                       tag=this_tag.id,
                                                       measurement_instance=this_inst.id)

    def crontab_command(self, action, command, interval):
        ''' manage cronjob entries for netspryte '''
        cron = crontab.CronTab(user='root')
        if action == 'show':
            return self.crontab_command_show(command)
        elif action == 'delete':
            return self.crontab_command_delete(command, interval)
        elif action == 'add':
            return self.crontab_command_add(command, interval)

    def crontab_command_show(self, command):
        cron = crontab.CronTab(user='root')
        if not command or command == 'all':
            for cron_job in cron:
                logging.warn(cron_job)
        else:
            for cron_job in cron.find_command(command):
                logging.warn(cron_job)

    def crontab_command_add(self, command, interval):
        time_min_regex = "(\d+)m"
        time_hour_regex = "(\d+)h"
        cron = crontab.CronTab(user='root')
        cron_job = cron.new(command)
        if re.search(time_min_regex, interval):
            t = int(re.sub(r'\D', "", interval))
            if (t < 1 or t > 59):
                logging.error("incorrect minute value; must be between 1 and 59")
                return
            cron_job.minute.every(t)
        elif re.search(time_hour_regex, interval):
            t = int(re.sub(r'\D', "", interval))
            if (t < 0 or t > 23):
                logging.error("incorrect hour value; must be between 0 and 23")
                return
            cron_job.hour.every(t)
        else:
            logging.error("unrecognized time interval; format examples: 1m, 5m, or 1h")
            return
        cron.write()
        logging.warn("new cronjob: %s", cron.render())

    def crontab_command_delete(self, command, interval):
        cron = crontab.CronTab(user='root')
        for cron_job in cron.find_command(command):
            logging.warn("removing cron job: %s", cron_job)
            cron.remove(cron_job)
            cron.write()
