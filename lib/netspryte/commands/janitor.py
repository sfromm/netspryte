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

import netspryte
from netspryte.manager import *

from netspryte.commands import BaseCommand
from netspryte import constants as C
from netspryte.utils import *

class JanitorCommand(BaseCommand):

    def __init__(self, daemonize=False):
        super(JanitorCommand, self).__init__(daemonize)
        group1 = self.parser.add_argument_group('Tag', 'Tag measurement instances')
        group1.add_argument('-i', '--instance', action='append',
                            help='measurement instance to tag')
        group1.add_argument('-t', '--tag', action='append',
                            help='tag name')
        self.parser.add_argument('command', type=str,
                                 choices=['tag'],
                                 help="Sub-command")

    def run(self):
        args = self.parser.parse_args()
        setup_logging(args.verbose)
        self.mgr = Manager()
        if args.command == 'tag':
            self.tag_command(args.tag, args.instance)

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
