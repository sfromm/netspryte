# Written by Stephen Fromm <stephenf nero net>
# (C) 2015-2016 University of Oregon
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
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
import re

from netspryte.commands import BaseCommand
from netspryte import constants as C
from netspryte.utils import *
from netspryte.db.rrd import *

class RrdTuneCommand(BaseCommand):

    def __init__(self, daemonize=False):
        super(RrdTuneCommand, self).__init__(daemonize)
        self.parser.add_argument('--file',
                                 help='Path to RRD to tune')
        self.parser.add_argument('-n', '--dryrun',
                                 action="store_true", default=False,
                                 help="Perform dryrun.  Do not make changes")

    def run(self):
        args = self.parser.parse_args()
        setup_logging(args.verbose)
        cfg = C.load_config()
        rrd_xml = list()
        rrd_path = args.file
        xml_path = rrd_path.replace('rrd', 'xml')
        json_path = rrd_path.replace('rrd', 'json')
        data = parse_json_from_file(json_path)

        info = rrd_info(rrd_path)
        try:
            if '_class' in data and data['_class'] == 'interface':
                ds_max = int(data['ifSpeed'])
                if ds_max == ( 2**32 - 1):
                    ds_max = int(data['ifHighSpeed']) * 10**6
                if ds_max == 0:
                    ds_max = 40 * 10**9
                rrd_tune_ds_max(rrd_path, ds_max)
        except KeyError as e:
            logging.error("failed to look up key: %s", e)

