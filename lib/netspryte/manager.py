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
import logging
import pymongo
import traceback
from bson.objectid import ObjectId

from netspryte import constants as C


class Manager(object):
    ''' data store manager object '''

    def __init__(self, **kwargs):
        ''' initialize manager object '''
        name = kwargs.get('name', C.DEFAULT_MONGO_NAME)
        host = kwargs.get('host', C.DEFAULT_MONGO_HOST)
        port = kwargs.get('port', C.DEFAULT_MONGO_PORT)

        self.client = pymongo.MongoClient(host, port)
        self.db = self.client[name]
        self.name = name
        self.host = host
        self.port = port
        self.create_collections()

    def create_collections(self):
        ''' create collections if they do not exist '''
        self.host_collection = self.db.host
        self.measurement_class_collection = self.db.measurement_class
        self.measurement_instance_collection = self.db.measurement_instance

    def drop_collections(self):
        self.db.drop_collection("host")
        self.db.drop_collection("measurement_class")
        self.db.drop_collection("measurement_instance")

    def close(self):
        ''' close connection -- noop '''
        pass

    def get(self, collection, **kwargs):
        ''' get an object '''
        data = None
        try:
            data = collection.find_one(kwargs)
        except Exception as e:
            logging.warn("failed to look up document: %s", str(e))
        return data

    def get_all(self, collection):
        data = None
        try:
            data = collection.find()
        except Exception as e:
            logging.error("failed to retrieve collection: %s", str(e))
        return data

    def get_or_create(self, collection, **kwargs):
        ''' get or create an object '''
        logging.debug("getting or creating object")
        document = dict()
        logging.debug("get_or_create %s %s", collection, kwargs['name'])
        document = self.update(collection, document, **kwargs)
        return document

    def save_host(self, document, **kwargs):
        ''' update/save a host document '''
        return self.update(self.host_collection, document, **kwargs)

    def save_measurement_class(self, document, **kwargs):
        ''' update/save a measurement_class document '''
        return self.update(self.measurement_class_collection, document, **kwargs)

    def save_measurement_instance(self, document, **kwargs):
        ''' update/save a measurement_instance document '''
        return self.update(self.measurement_instance_collection, document, **kwargs)

    def update(self, collection, document, **kwargs):
        ''' update an object '''
        for k, v in list(kwargs.items()):
            if isinstance(v, dict):
                # This is a mongo document; use just the objectId
                if '_id' in v and isinstance(v['_id'], ObjectId):
                    v = v['_id']
            document[k] = v
        logging.debug("updating %s", document['name'])
        if 'lastseen' not in kwargs:
            document['lastseen'] = datetime.datetime.now()

        document = collection.find_one_and_update({"name": document["name"]},
                                                  {"$set": document}, upsert=True,
                                                  return_document=pymongo.ReturnDocument.AFTER)
        logging.debug("updated %s", document['name'])
        return document

    def get_instances(self, key, val, paginated=False):
        ''' return measurement instances where key equals value '''
        qry = self.measurement_instance_collection.find({key: val})
        if paginated:
            return qry
        else:
            return [q for q in qry]

    def get_instances_by_host(self, arg, paginated=False):
        '''
        Return list of measurement instances based on the associated host.
        If paginated is True, return a peewee Query object.
        '''
        host = self.host_collection.find({'name': arg})
        return self.get_instances("host", host['_id'])

    def get_instances_by_class(self, arg, paginated=False):
        '''
        Return list of measurement instances based on the measurement class.
        If paginated is True, return a peewee Query object.
        '''
        cls = self.measurement_class_collection.find({'name': arg})
        return self.get_instances("measurement_class", cls['_id'])

    def get_instances_by_attribute(self, key, val, paginated=False):
        '''
        Return list of measurement instances based on a matching attribute value.
        If paginated is True, return a peewee Query object.
        '''
        return self.get_instances("attrs.%s" % key, val)

    def get_instances_by_presentation(self, key, val, paginated=False):
        '''
        Return list of measurement instances based on a matching presentation value.
        If paginated is True, return a peewee Query object.
        '''
        return self.get_instances("presentation.%s" % key, val)

    def get_instances_by_tags(self, tags, paginated=False):
        '''
        Return list of measurement instances based on associated tags.
        If paginated is True, return a peewee Query object.
        '''
        return self.get_instances("tags", {"$in": [tags]})
