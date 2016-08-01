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
from netspryte.rrd import *

class RrdFeedRrdCommand(BaseCommand):

    def __init__(self, daemonize=False):
        super(RrdFeedRrdCommand, self).__init__(daemonize)
        self.parser.add_argument('--src',
                                 help='Path to pull RRD data from')
        self.parser.add_argument('--dst',
                                 help='Destination RRD to feed data to')
        self.parser.add_argument('--map', action="append",
                                 help='Map DS from source to DS in dest')

    def run(self):
        args = self.parser.parse_args()
        setup_logging(args.verbose)
        cfg = C.load_config()
        src_path = args.src
        dst_path = args.dst
        if not src_path or not dst_path:
            logging.error("missing required option")
            return 1
#        if not os.path.exists(src_path) or not os.path.exists(dst_path):
#            logging.error("missing required rrd")
#            return 1
#        os.rename(dst_path, '{0}.bak'.format(dst_path))
        all_rra_db = list()
        rra_db = list()
        is_database = False
        date = None
        for line in rrd_dump(src_path):
            line = line.rstrip()
            if re.match('\s*</database>', line):
                is_database = False
                all_rra_db.append(rra_db)
                rra_db = list()
            elif is_database:
                match = re.search('\s*<!-- (\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d ... . \d+) --> <row><v>(.*)</v></row>', line)
                date = match.group(1)
                values = match.group(2).split('</v><v>')
                rra_db.append( (date, values) )
            elif re.match('\s*<database>', line):
                is_database = True

