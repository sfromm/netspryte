# Written by Stephen Fromm <stephenf nero net>
# (C) 2015 University of Oregon

# This file is part of netspryte
#
# netspryte is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# netspryte is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with netspryte.  If not, see <http://www.gnu.org/licenses/>.

import unittest
import json
import os
import sys

import netspryte
import netspryte.snmp
from netspryte import constants as C
from netspryte.errors import *


class TestConstants(unittest.TestCase):

    def setUp(self):
        self.msnmp = netspryte.snmp.SNMPSession()

    def test_constants_missing_config(self):
        os.environ['NETSPRYTE_CONFIG'] = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                      'missing-netspryte.cfg')
        C.load_config()

    def test_constants_bad_config(self):
        os.environ['NETSPRYTE_CONFIG'] = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                      'bad-netspryte.cfg')
        with self.assertRaises(NetspryteError):
            C.load_config()

    def test_constants_good_config(self):
        os.environ['NETSPRYTE_CONFIG'] = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                      'netspryte.cfg')
        C.load_config()
