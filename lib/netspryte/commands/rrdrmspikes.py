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

class RrdRemoveSpikesCommand(BaseCommand):

    def __init__(self, daemonize=False):
        super(RrdRemoveSpikesCommand, self).__init__(daemonize)
        self.parser.add_argument('--file',
                                 help='Path to RRD to remove spikes from')
        self.parser.add_argument('-t', '--datetime',
                                 help='A regular expression for a date to limit '
                                 'the range to operate on.  The format should be YYYY-MM-DD hh:mm')
        self.parser.add_argument('-x', '--exponent', type=int, default=9,
                                 help='Replace values that have exponents larger than <exponent>. '
                                 'Default is 9')
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
        info = rrd_info(rrd_path)
        for line in rrd_dump(rrd_path):
            line = line.rstrip()
            if re.match('\s*.*<row><v>', line):
                if args.datetime and not re.match(r'\s*<!-- %s' % args.datetime, line):
                    rrd_xml.append(line)
                    continue
                new_values = list()
                values = line.split('<v>')
                rowtime = ""
                for value in values:
                    if '<row>' in value or 'NaN' in value:
                        m = re.match(r"\s*<!-- ([\d-]+ [\d:]+ ...) /", value)
                        if m:
                            rowtime = m.group(1)
                        new_values.append(value)
                        continue
                    m = re.match(r"([\d\.]+)e[-\+](\d+).*", value)
                    if not m:
                        new_values.append(value)
                        logging.warn("failed to match value: %s", value)
                        continue
                    val = m.group(1)
                    exp = m.group(2)
                    if int(exp) > args.exponent:
                        logging.info("found %se%s exceeds exponent limit %s at %s",
                                     val, exp, args.exponent, rowtime)
                        new_values.append("NaN</v>")
                    else:
                        new_values.append(value)
                line = "<v>".join(new_values)
            rrd_xml.append(line)
        with open(xml_path, 'w') as xml:
            xml.write("\n".join(rrd_xml))
        if args.dryrun:
            logging.info("performing dryrun; not making changes")
            return 0
        rrd_preserve(rrd_path)
        rrd_restore(xml_path, rrd_path)

