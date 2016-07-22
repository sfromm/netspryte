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
from snmpryte.snmp.host.interface import HostInterface
import snmpryte.db.influx

class TestDatabase(unittest.TestCase):

    def setUp(self):
        self.msnmp = snmpryte.snmp.SNMPSession()
        self.hostintf = HostInterface(self.msnmp)
        self.dbs = list()

    def test_db_influxdb_port_is_integer(self):
        db = snmpryte.db.influx.InfluxDatabaseBackend('influxdb')
        self.assertEqual(db.influxdb_port, C.DEFAULT_INFLUXDB_PORT)

    def test_db_influxdb_create(self):
        db = snmpryte.db.influx.InfluxDatabaseBackend('influxdb', host=self.msnmp.host,
                                                      influxdb_host=C.DEFAULT_INFLUXDB_HOST,
                                                      influxdb_user=C.DEFAULT_INFLUXDB_USER,
                                                      influxdb_password=C.DEFAULT_INFLUXDB_PASSWORD,
                                                      influxdb_database=C.DEFAULT_INFLUXDB_DATABASE)
        self.assertTrue(hasattr(db, 'client'))

    def test_db_influxdb_write(self):
        db = snmpryte.db.influx.InfluxDatabaseBackend('influxdb', host=self.msnmp.host,
                                                      influxdb_host=C.DEFAULT_INFLUXDB_HOST,
                                                      influxdb_user=C.DEFAULT_INFLUXDB_USER,
                                                      influxdb_password=C.DEFAULT_INFLUXDB_PASSWORD,
                                                      influxdb_database=C.DEFAULT_INFLUXDB_DATABASE)
        for key, data in self.hostintf.data.iteritems():
            db.write(data)
