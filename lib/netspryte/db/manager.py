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

import datetime
import os
import logging
import subprocess
import traceback

from netspryte import constants as C
from netspryte.db.model import *

import peewee
from playhouse.postgres_ext import *
from playhouse.shortcuts import model_to_dict, dict_to_model

peewee_logger = logging.getLogger('peewee')
peewee_logger.addHandler(logging.StreamHandler())

class Manager(object):
    ''' db manager object '''

    def __init__(self, **kwargs):
        ''' initialize manager object '''
        engine = kwargs.get('engine', C.DEFAULT_DB_ENGINE)
        name   = kwargs.get('name', C.DEFAULT_DB_NAME)
        host   = kwargs.get('host', C.DEFAULT_DB_HOST)
        user   = kwargs.get('user', C.DEFAULT_DB_USER)
        passwd = kwargs.get('pass', C.DEFAULT_DB_PASS)

        self.engine = engine
        self.name = name

        if 'sqlite' in engine:
            # http://docs.peewee-orm.com/en/latest/peewee/database.html?#additional-connection-initialization
            database = SqliteDatabase(name, threadlocals=True, pragmas=(
                ('journal_mode', 'WAL'),
                ('foreign_keys', 'ON'),
            ))
        elif 'postgres' in engine:
            database = PostgresqlExtDatabase(name, register_hstore=False, user=user, password=passwd, host=host)
        else:
            database = None

        DB_PROXY.initialize(database)
        self.database = database
        try:
            self.database.connect()
        except OperationalError as e:
            logging.error("failed to open database %s", name)
            raise
        self.create_tables()

    def create_tables(self):
        ''' create tables if they do not exist '''
        Host.create_table(fail_silently=True)
        MeasurementClass.create_table(fail_silently=True)
        MeasurementInstance.create_table(fail_silently=True)

    def execute(self, modquery, nocommit=False):
        ''' execute a model query; returns number of rows affected '''
        r = modquery.execute()
        return r

    def close(self):
        ''' close connection to database '''
        self.database.close()

    def save(self, modinst, nocommit=False):
        ''' save an object '''
        modinst.save()

    def get(self, model, **kwargs):
        ''' get an object '''
        data = None
        try:
            data = model.get(**kwargs)
        except peewee.DoesNotExist as e:
            logging.warn("failed to look up object")
        return data

    def get_all(self, model):
        data = None
        try:
            data = model.select()
        except Exception as e:
            logging.error("failed to retrieve model")
        return data

    def get_or_create(self, model, **kwargs):
        ''' get or create an object '''
        logging.debug("getting or creating object")
        instance = None
        try:
            ( instance, created ) = model.get_or_create(**kwargs)
            self.save(instance)
        except peewee.DatabaseError as e:
            logging.error("error while attempting to update database: %s", traceback.format_exc())
        except peewee.DatabaseError as e:
            logging.error("error while attempting to update database: %s", traceback.format_exc())
        return instance

    def update(self, modinst, **kwargs):
        ''' update an object '''
        updated = False
        for k, v in kwargs:
            if hasattr(modinst, k):
                setattr(modinst, k, v)
        if hasattr(modinst, 'lastseen'):
            modinst.lastseen = datetime.datetime.now()
        self.save(modinst)

    def to_dict(self, modinst):
        return model_to_dict(modinst)

    def get_instances(self, key, val):
        ''' return measurement instances where key equals value '''
        result = list()
        for q in MeasurementInstance.select().where(getattr(MeasurementInstance, key) == val):
            result.append(q)
        return result

    def get_instances_by_host(self, arg):
        ''' blah '''
        result = list()
        host = self.get(Host, name=arg)
        for q in MeasurementInstance.select().join(Host).where(MeasurementInstance.host == host):
            result.append(q)
        return result

    def get_instances_by_attribute(self, key, val):
        ''' blah '''
        result = list()
        for q in MeasurementInstance.select().where(
                MeasurementInstance.attrs[key].startswith(val)):
            result.append(q)
        return result

    def get_instances_by_presentation(self, key, val):
        ''' blah '''
        result = list()
        for q in MeasurementInstance.select().where(
                MeasurementInstance.presentation[key].startswith(val)):
            result.append(q)
        return result
