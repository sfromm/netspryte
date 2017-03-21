# Written by Stephen Fromm <stephenf nero net>
# Copyright (C) 2015-2017 University of Oregon

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
from netspryte.snmp.host.interface import HostInterface
import netspryte.db.influx

class TestDatabase(unittest.TestCase):

    def setUp(self):
        self.msnmp = netspryte.snmp.SNMPSession()
        self.hostintf = HostInterface(self.msnmp)
        self.dbs = list()

    def test_db_influxdb_port_is_integer(self):
        db = netspryte.db.influx.InfluxDatabaseBackend('influxdb')
        self.assertEqual(db.port, C.DEFAULT_INFLUXDB_PORT)

    def test_db_influxdb_create(self):
        db = netspryte.db.influx.InfluxDatabaseBackend('influxdb',
                                                       host=C.DEFAULT_INFLUXDB_HOST,
                                                       user=C.DEFAULT_INFLUXDB_USER,
                                                       password=C.DEFAULT_INFLUXDB_PASSWORD,
                                                       database=C.DEFAULT_INFLUXDB_DATABASE)
        self.assertTrue(hasattr(db, 'client'))

    def test_db_influxdb_write(self):
        db = netspryte.db.influx.InfluxDatabaseBackend('influxdb',
                                                       host=C.DEFAULT_INFLUXDB_HOST,
                                                       user=C.DEFAULT_INFLUXDB_USER,
                                                       password=C.DEFAULT_INFLUXDB_PASSWORD,
                                                       database=C.DEFAULT_INFLUXDB_DATABASE)
        for data in self.hostintf.data:
            db.write(data)

    def test_db_mongodb_port_is_integer(self):
        db = netspryte.db.mongo.MongoDatabaseBackend('mongodb')
        self.assertEqual(db.port, C.DEFAULT_MONGODB_PORT)

    def test_db_mongodb_create(self):
        db = netspryte.db.mongo.MongoDatabaseBackend('mongodb',
                                                     host=C.DEFAULT_MONGODB_HOST,
                                                     database=C.DEFAULT_MONGODB_DATABASE)
        self.assertTrue(hasattr(db, 'db'))

    def test_db_mongodb_write(self):
        db = netspryte.db.mongo.MongoDatabaseBackend('mongodb',
                                                     host=C.DEFAULT_MONGODB_HOST,
                                                     database=C.DEFAULT_MONGODB_DATABASE)
        for data in self.hostintf.data:
            db.write(data)
