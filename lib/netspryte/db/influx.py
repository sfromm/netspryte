# Written by Stephen Fromm <stephenf nero net>
# (C) 2016 University of Oregon
#
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

import os
import logging
import time
import subprocess

from netspryte.db import *
import netspryte.snmp
from netspryte import constants as C

try:
    import influxdb
    HAVE_INFLUXDB = True
except ImportError:
    HAVE_INFLUXDB = False

class InfluxDatabaseBackend(BaseDatabaseBackend):

    TIME_PRECISION = 's'

    def __init__(self, backend, **kwargs):
        super(InfluxDatabaseBackend, self).__init__(backend, **kwargs)
        self.client = None
        if not HAVE_INFLUXDB:
            logging.error("do not have influxdb bindings for python")
            return None
        self.influxdb_host = kwargs.get('influxdb_host', C.DEFAULT_INFLUXDB_HOST)
        self.influxdb_port = kwargs.get('influxdb_port', C.DEFAULT_INFLUXDB_PORT)
        self.influxdb_database = kwargs.get('influxdb_database', C.DEFAULT_INFLUXDB_DATABASE)
        self.influxdb_user = kwargs.get('influxdb_user', C.DEFAULT_INFLUXDB_USER)
        self.influxdb_password = kwargs.get('influxdb_password', C.DEFAULT_INFLUXDB_PASSWORD)
        self.client = influxdb.InfluxDBClient(self.influxdb_host, self.influxdb_port,
                                              self.influxdb_user, self.influxdb_password, self.influxdb_database)
        logging.warn("influx host is %s", self.influxdb_host)
        databases = influxdb_list_databases(self.client)
        if self.influxdb_database not in databases:
            influxdb_create_database(self.client, self.influxdb_database)

    def write(self, data):
        ''' write data to rrd database '''
        if not self.client:
            return None
        influxdb_switch_database(self.client, self.influxdb_database)
        return influxdb_write(self.client, data, self.host)

    @property
    def influxdb_host(self):
        return self._influxdb_host

    @influxdb_host.setter
    def influxdb_host(self, arg):
        self._influxdb_host = arg

    @property
    def influxdb_port(self):
        return self._influxdb_port

    @influxdb_port.setter
    def influxdb_port(self, arg):
        self._influxdb_port = arg

    @property
    def influxdb_database(self):
        return self._influxdb_database

    @influxdb_database.setter
    def influxdb_database(self, arg):
        self._influxdb_database = arg

    @property
    def influxdb_user(self):
        return self._influxdb_user

    @influxdb_user.setter
    def influxdb_user(self, arg):
        self._influxdb_user = arg

    @property
    def influxdb_password(self):
        return self._influxdb_password

    @influxdb_password.setter
    def influxdb_password(self, arg):
        self._influxdb_password = arg

def influxdb_create_database(client, dbname):
    try:
        logging.info("creating database %s", dbname)
        client.create_database(dbname)
        influxdb_switch_database(client, dbname)
    except ConnectionError as e:
        logging.error("failed to create database %s: %s", dbname, str(e))\

def influxdb_switch_database(client, dbname):
    logging.info("switching to database %s", dbname)
    client.switch_database(dbname)

def influxdb_list_databases(client):
    dbs = client.get_list_database()
    return [ x['name'] for x in dbs ]

def influxdb_write(client, data, host="localhost", ts=time.time()):
    points = list()
    data_class = data.get('_class', 'NA')
    data_title = data.get('_title', 'NA')
    data_id = data.get('_id', 'NA')
    for k, v in data.iteritems():
        if k.startswith('_'):
            continue
        if hasattr(v, 'prettyPrint'):
            v = v.prettyPrint()
        point = {
            "measurement": data_class,
            "time": int(ts),
            "tags": {
                "host"  : host,
                "title" : data_title,
                "instance" : data_id,
                "type": k.lower()
            },
            "fields": {
                "value": v
            }
        }
        points.append(point)
    try:
        client.write_points(points, time_precision=InfluxDatabaseBackend.TIME_PRECISION)
    except influxdb.exceptions.InfluxDBClientError as e:
        logging.error("failed to write data: %s", str(e))
