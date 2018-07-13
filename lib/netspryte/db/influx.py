# Written by Stephen Fromm <stephenf nero net>
# Copyright (C) 2016-2017 University of Oregon
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
        self.host = kwargs.get('host', C.DEFAULT_INFLUXDB_HOST)
        self.port = kwargs.get('port', C.DEFAULT_INFLUXDB_PORT)
        self.database = kwargs.get('database', C.DEFAULT_INFLUXDB_DATABASE)
        self.user = kwargs.get('user', C.DEFAULT_INFLUXDB_USER)
        self.password = kwargs.get('password', C.DEFAULT_INFLUXDB_PASSWORD)
        self.client = influxdb.InfluxDBClient(self.host, self.port,
                                              self.user, self.password, self.database)
        logging.warn("influx host is %s", self.host)
        databases = influxdb_list_databases(self.client)
        if self.database not in databases:
            influxdb_create_database(self.client, self.database)

    def write(self, data):
        ''' write data to rrd database '''
        if not self.client:
            return None
        influxdb_switch_database(self.client, self.database)
        return influxdb_write(self.client, data)

    @property
    def host(self):
        return self._host

    @host.setter
    def host(self, arg):
        self._host = arg

    @property
    def port(self):
        return self._port

    @port.setter
    def port(self, arg):
        try:
            self._port = int(arg)
        except ValueError:
            raise ValueError("InflubDB port must be an integer")

    @property
    def database(self):
        return self._database

    @database.setter
    def database(self, arg):
        self._database = arg

    @property
    def user(self):
        return self._user

    @user.setter
    def user(self, arg):
        self._user = arg

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, arg):
        self._password = arg

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

def influxdb_write(client, data, ts=time.time()):
    points = list()
    data_class = data.measurement_class.name
    data_title = data.presentation.title
    data_id = data.name
    data_host = data.host.name
    for k, v in list(data.items()):
        if k.startswith('_'):
            continue
        if hasattr(v, 'prettyPrint'):
            v = v.prettyPrint()
        point = {
            "measurement": data_class,
            "time": int(ts),
            "tags": {
                "host"  : data_host,
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
