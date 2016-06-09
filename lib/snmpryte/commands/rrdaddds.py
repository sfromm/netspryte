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

from snmpryte.commands import BaseCommand
from snmpryte import constants as C
from snmpryte.utils import *
from snmpryte.rrd import *

class RrdAddDsCommand(BaseCommand):

    def __init__(self, daemonize=False):
        super(RrdAddDsCommand, self).__init__(daemonize)
        self.parser.add_argument('--file',
                                 help='Path to RRD to add DS to')
        self.parser.add_argument('--name',
                                 help='Name of data source (DS)')
        self.parser.add_argument('--type',
                                 help='Type of DS to add (eg Gauge, Counter)')
        self.parser.add_argument('-n', '--dryrun',
                                 action="store_true", default=False,
                                 help="Perform dryrun.  Do not make changes")

    def run(self):
        args = self.parser.parse_args()
        setup_logging(args.verbose)
        cfg = C.load_config()
        rrd_xml = list()
        is_database = False
        rrd_path = args.file
        dsname = args.name
        dstype = args.type
        if not dsname or not dstype:
            logging.error("missing required option")
            return 1
        dstype = dstype.upper()
        xml_path = rrd_path.replace('rrd', 'xml')
        heartbeat = C.DEFAULT_RRD_STEP * C.DEFAULT_RRD_HEARTBEAT
        info = rrd_info(rrd_path)
        if 'ds[{0}].type'.format(dsname) in info:
            logging.error("DS %s appears to already be present", dsname)
            return 0
        for line in rrd_dump(rrd_path):
            line = line.rstrip()
            if re.match('\s*<!-- Round Robin Archives -->', line):
                rrd_xml.append("<ds>")
                rrd_xml.append("   <name> {0} </name>".format(dsname))
                rrd_xml.append("   <type> {0} </type>".format(dstype))
                rrd_xml.append("   <minimal_heartbeat> {0} </minimal_heartbeat>".format(heartbeat))
                rrd_xml.append("   <min> NaN </min>")
                rrd_xml.append("   <max> NaN </max>")
                rrd_xml.append("   <!-- PDP Status -->")
                rrd_xml.append("   <last_ds> UNKN </last_ds>")
                rrd_xml.append("   <unknown_sec> 0 </unknown_sec>")
                rrd_xml.append("</ds>")
            elif re.match('\s*</cdp_prep>', line):
                rrd_xml.append("<ds>")
                rrd_xml.append("   <primary_value> 0.0000000000e+00 </primary_value>")
                rrd_xml.append("   <secondary_value> 0.0000000000e+00 </secondary_value>")
                rrd_xml.append("   <value> NaN </value>")
                rrd_xml.append("   <unknown_datapoints> 0 </unknown_datapoints>")
                rrd_xml.append("</ds>")
            elif re.match('\s*</database>', line):
                is_database = False
            elif is_database:
                line = re.sub('</row>', '<v> NaN </v></row>', line)

            rrd_xml.append(line)
            if re.match('\s*<database>', line):
                is_database = True
        with open(xml_path, 'w') as xml:
            xml.write("\n".join(rrd_xml))
        if args.dryrun:
            logging.info("performing dryrun; not making changes")
            return 0
        os.rename(rrd_path, "{0}.bak".format(rrd_path))
        rrd_restore(xml_path, rrd_path)

