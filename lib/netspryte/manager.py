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

import datetime
import os
import logging
import operator
import subprocess
import traceback

from netspryte import constants as C
from netspryte.model import *

import peewee
from playhouse.postgres_ext import *
from playhouse.shortcuts import model_to_dict, dict_to_model

peewee_logger = logging.getLogger('peewee')
peewee_logger.addHandler(logging.StreamHandler())


def build_clause(cls, col, val, timeop=operator.lt):
    clause = None
    if not hasattr(cls, col):
        logging.warn('%s does not have the attribute %s', cls, col)
        return clause
    logging.debug("building filter clause %s:%s", col, val)
    if isinstance(val, list):
        clause = getattr(cls, col) << val
    else:
        if isinstance(getattr(cls, col), peewee.DateTimeField):
            clause = timeop(getattr(cls, col), val)
        else:
            clause = getattr(cls, col) == val
    return clause


class Manager(object):
    ''' db manager object '''

    def __init__(self, **kwargs):
        ''' initialize manager object '''
        engine = kwargs.get('engine', C.DEFAULT_DB_ENGINE)
        name   = kwargs.get('name', C.DEFAULT_DB_NAME)
        host   = kwargs.get('host', C.DEFAULT_DB_HOST)
        user   = kwargs.get('user', C.DEFAULT_DB_USER)
        passwd = kwargs.get('pass', C.DEFAULT_DB_PASS)
        create = kwargs.get('create', True)

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
        if create:
            self.create_tables()

    def create_tables(self):
        ''' create tables if they do not exist '''
        models = BaseModel.__subclasses__()
        self.database.create_tables(models, fail_silently=True)

    def execute(self, modquery, nocommit=False):
        ''' execute a model query; returns number of rows affected '''
        r = modquery.execute()
        return r

    def close(self):
        ''' close connection to database '''
        self.database.close()

    def save(self, modinst, nocommit=False):
        ''' save an object '''
        try:
            logging.debug("saving %s", str(modinst))
            modinst.save()
            logging.debug("done saving %s", str(modinst))
        except peewee.DataError:
            logging.error("error with the data for %s while attempting to update database: %s", modinst.name, traceback.format_exc())
        except peewee.DatabaseError:
            logging.error("error while attempting to update database: %s", traceback.format_exc())

    def get(self, model, **kwargs):
        ''' get an object '''
        data = None
        try:
            data = model.get(**kwargs)
        except peewee.DoesNotExist:
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
            name = ""
            if 'name' in kwargs:
                name = kwargs['name']
            logging.debug("get_or_create %s %s", model, name)
            (instance, created) = model.get_or_create(**kwargs)
            self.save(instance)
        except peewee.DatabaseError as e:
            logging.error("error while attempting to update database: %s", traceback.format_exc())
        return instance

    def delete(self, model, query):
        ''' delete instances of a model '''
        logging.debug("deleting object(s)")
        count = 0
        if not query:
            logging.warn("skipping deletion with empty query")
            return count
        try:
            q = model.delete().where(query)
            count = q.execute()
            logging.info("deleted %s entries", count)
        except peewee.DatabaseError as e:
            logging.error("error while attempting to delete from database: %s", traceback.format_exc())
        return count

    def update(self, modinst, **kwargs):
        ''' update an object '''
        updated = False
        logging.debug("updating %s", str(modinst))
        for k, v in list(kwargs.items()):
            if hasattr(modinst, k):
                setattr(modinst, k, v)
        if hasattr(modinst, 'lastseen'):
            modinst.lastseen = datetime.datetime.now()
        self.save(modinst)
        logging.debug("done updating %s", str(modinst))

    def to_dict(self, modinst):
        return model_to_dict(modinst)

    def get_instances(self, key, val, paginated=False):
        ''' return measurement instances where key equals value '''
        qry = MeasurementInstance.select().where(getattr(MeasurementInstance, key) == val)
        if paginated:
            return qry
        else:
            return [ q for q in qry ]

    def get_instances_by_host(self, arg, paginated=False):
        '''
        Return list of measurement instances based on the associated host.
        If paginated is True, return a peewee Query object.
        '''
        host = self.get(Host, name=arg)
        qry = MeasurementInstance.select().join(Host).where(MeasurementInstance.host == host)
        if paginated:
            return qry
        else:
            return [ q for q in qry ]

    def get_instances_by_class(self, arg, paginated=False):
        '''
        Return list of measurement instances based on the measurement class.
        If paginated is True, return a peewee Query object.
        '''
        cls = self.get(MeasurementClass, name=arg)
        qry = MeasurementInstance.select().join(Host).where(MeasurementInstance.measurement_class == cls)
        if paginated:
            return qry
        else:
            return [ q for q in qry ]

    def get_instances_by_attribute(self, key, val, paginated=False):
        '''
        Return list of measurement instances based on a matching attribute value.
        If paginated is True, return a peewee Query object.
        '''
        qry = MeasurementInstance.select().where(MeasurementInstance.attrs[key].startswith(val))
        if paginated:
            return qry
        else:
            return [ q for q in qry ]

    def get_instances_by_title(self, arg, paginated=False):
        '''
        Return list of measurement instances based on a matching presentation value.
        If paginated is True, return a peewee Query object.
        '''
        qry = MeasurementInstance.select().where(MeasurementInstance.title.startswith(arg))
        if paginated:
            return qry
        else:
            return [q for q in qry]

    def get_instances_by_tags(self, tags, paginated=False):
        '''
        Return list of measurement instances based on associated tags.
        If paginated is True, return a peewee Query object.
        '''
        qry = (MeasurementInstance.select()
               .join(MeasurementInstanceTag)
               .join(Tag)
               .where((Tag.name << tags))
               .group_by(MeasurementInstance))
        if paginated:
            return qry
        else:
            return [ q for q in qry ]

    def get_instance_attributes(self, measurement_instance):
        '''
        Return attributes related to this measurement instance.
        '''
        m = getattr(measurement_instance, "%s_attrs" % (measurement_instance.measurement_class.name)).get()
        return m

    def get_instance_metrics(self, measurement_instance):
        '''
        Return metrics related to this measurement instance.
        '''
        m = getattr(measurement_instance, "%s_metrics" % (measurement_instance.measurement_class.name)).get()
        return m
