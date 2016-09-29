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
import glob
import pprint

import netspryte
import netspryte.snmp
from netspryte.snmp.host.interface import HostInterface
from netspryte.snmp.vendor.cisco.cbqos import CiscoCBQOS

from netspryte.commands import BaseCommand
from netspryte import constants as C
from netspryte.utils import *

class DiscoverCommand(BaseCommand):

    def __init__(self, daemonize=False):
        super(DiscoverCommand, self).__init__(daemonize)
        self.parser.add_argument('devices', type=str, nargs='*',
                                 default=C.DEFAULT_DEVICES,
                                 help='list of devices to query')

    def run(self):
        args = self.parser.parse_args()
        setup_logging(args.verbose)
        logging.debug("beginning discovery")
        for device in args.devices:
            process_device(device, args)


def process_device(device, args):
    try:
        msnmp = netspryte.snmp.SNMPSession(host=device)
        cbqos = CiscoCBQOS(msnmp)
        for key, data in cbqos.interfaces.iteritems():
            pprint.pprint({key: data})
        for key, data in cbqos.data.iteritems():
            pprint.pprint({key: data})
    except TypeError as e:
        logging.error("encountered error with %s; skipping to next device: %s", device, str(e))

