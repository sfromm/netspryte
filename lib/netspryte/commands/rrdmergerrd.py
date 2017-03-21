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

class RrdMergeRrdCommand(BaseCommand):

    def __init__(self, daemonize=False):
        super(RrdMergeRrdCommand, self).__init__(daemonize)
        self.parser.description = "Take a list of RRDs and consolidate values into single RRD."
        self.parser.add_argument('-n', '--dryrun',
                                 action="store_true", default=False,
                                 help="Perform dryrun.  Do not make changes")
        self.parser.add_argument('-f', '--file',
                                 help='Path to merged destination RRD')
        self.parser.add_argument('rrds', type=str, nargs='*',
                                 help='List of RRD files to merge')

    def run(self):
        ''' main '''
        args = self.parser.parse_args()
        setup_logging(args.verbose)
        cfg = C.load_config()
        rrd_xml = list()

        rrd_data = dict()
        for i, rrd_path in enumerate(args.rrds):
            for line in rrd_dump(rrd_path):
                match = re.search(r"<cf>(.*)</cf>", line)
                if match:
                    cf = match.group(1)
                match = re.search(r"<pdp_per_row>(.*)</pdp_per_row>", line)
                if match:
                    pdp = match.group(1)

                match = re.search(r" / (\d+) --> (.*)", line)
                if match:
                    k = cf + pdp
                    rrd_data.setdefault(k, dict())
                    if ('NaN' not in match.group(2)) or (
                            match.group(1) not in rrd_data[k]):
                        rrd_data[k][match.group(1)] = line
                    line = rrd_data[k][match.group(1)]

                if rrd_path == args.rrds[-1]:
                    rrd_xml.append(line.rstrip())

        if not args.file:
            logging.error("no destination file to merge rrd to")
            return 0
        if args.dryrun:
            logging.info("performing dryrun; not making changes")
            return 0
        rrd_path = args.file
        xml_path = rrd_path + ".xml"
        with open(xml_path, 'w') as xml:
            xml.write("\n".join(rrd_xml))
        if os.path.exists(rrd_path):
            rrd_preserve(rrd_path)
        logging.info("restoring xml to %s", rrd_path)
        rrd_restore(xml_path, rrd_path)




