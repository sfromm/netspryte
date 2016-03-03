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

class TestSnmp(unittest.TestCase):

    def setUp(self):
        self.msnmp = snmpryte.snmp.SNMPSession()

    def test_snmp_port_is_not_integer(self):
        with self.assertRaises(ValueError):
            msnmp = snmpryte.snmp.SNMPSession(port="ghost")

    def test_snmp_port_is_integer(self):
        msnmp = snmpryte.snmp.SNMPSession(port="161")
        self.assertEqual(msnmp.port, 161)

    def test_snmp_version_is_bad(self):
        with self.assertRaises(ValueError):
            msnmp = snmpryte.snmp.SNMPSession(version="4", host="poop")

    def test_snmp_version_is_good(self):
        msnmp = snmpryte.snmp.SNMPSession(version="3")
        msnmp = snmpryte.snmp.SNMPSession(version="2c")

    def test_snmp_community_is_bad(self):
        with self.assertRaises(ValueError):
            msnmp = snmpryte.snmp.SNMPSession(community=4)

    def test_snmp_community_is_good(self):
        msnmp = snmpryte.snmp.SNMPSession(community="public")

    def test_snmp_level_is_bad(self):
        with self.assertRaises(ValueError):
            msnmp = snmpryte.snmp.SNMPSession(level="snarf")

    def test_snmp_level_is_good(self):
        msnmp = snmpryte.snmp.SNMPSession(level="authPriv")

    def test_snmp_get(self):
        msnmp = snmpryte.snmp.SNMPSession()
        self.assertEqual(isinstance(msnmp.get('1.3.6.1.2.1.1.5.0'), basestring), True)

    def test_snmp_walk(self):
        msnmp = snmpryte.snmp.SNMPSession()
        self.assertEqual(isinstance(
            msnmp.walk('1.3.6.1.2.1.31.1.1.1.1'), list
        ), True)
