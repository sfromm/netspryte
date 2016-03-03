#!/usr/bin/python

# Written by Stephen Fromm <stephenf nero net>
# (C) 2015 University of Oregon

# This file is part of snmpryte
#
# snmpryte is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# snmpryte is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with snmpryte.  If not, see <http://www.gnu.org/licenses/>.

import unittest
import json
import os
import sys

import snmpryte
import snmpryte.snmp
from snmpryte import constants as C
from snmpryte.errors import *


class TestConstants(unittest.TestCase):

    def setUp(self):
        self.msnmp = snmpryte.snmp.SNMPSession()

    def test_constants_missing_config(self):
        os.environ['SNMPRYTE_CONFIG'] = 'tests/missing-snmpryte.cfg'
        C.load_config()

    def test_constants_bad_config(self):
        os.environ['SNMPRYTE_CONFIG'] = 'tests/bad-snmpryte.cfg'
        with self.assertRaises(SnmpryteError):
            C.load_config()

    def test_constants_good_config(self):
        os.environ['SNMPRYTE_CONFIG'] = 'tests/snmpryte.cfg'
        C.load_config()
