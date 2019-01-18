# Written by Stephen Fromm <stephenf nero net>
# Copyright (C) 2018 University of Oregon

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

import re
import unittest
import pymongo

import netspryte
import netspryte.snmp
from netspryte import constants as C
from netspryte.snmp.host.interface import HostInterface
from netspryte.utils import json_ready


class TestMongo(unittest.TestCase):

    def setUp(self):
        self.mgr = netspryte.manager.Manager(name='testnetspryte')
        self.mgr.create_collections()
        self.msnmp = netspryte.snmp.SNMPSession()
        self.hostintf = HostInterface(self.msnmp)

    def test_manager_mongo_port_is_integer(self):
        self.assertEqual(self.mgr.port, C.DEFAULT_MONGO_PORT)

    def test_manager_has_collection_host(self):
        self.assertIsInstance(self.mgr.host_collection, pymongo.collection.Collection)

    def test_manager_save_host(self):
        host = self.hostintf.sysName
        self.assertIsInstance(self.mgr.get_or_create(self.mgr.host_collection, name=host), dict)

    def test_manager_save_measurement_collection(self):
        this_class = None
        for data in self.hostintf.data:
            this_class = self.mgr.get_or_create(self.mgr.measurement_class_collection,
                                                name=data['class'], transport=data['transport'])
            self.assertIsInstance(this_class, dict)

    def test_manager_update_measurement_collection(self):
        metric_types = dict()
        this_class = None
        for data in self.hostintf.data:
            this_class = self.mgr.get(self.mgr.measurement_class_collection, name=data['class'], transport=data['transport'])
            if not metric_types:
                for k, v in list(data['metrics'].items()):
                    metric_types[k] = netspryte.snmp.get_value_type(v)
        r = self.mgr.update(self.mgr.measurement_class_collection, this_class, metric_type=metric_types)
        self.assertIsInstance(r, dict)

    def test_manager_save_measurement_instance(self):
        this_class = None
        for data in self.hostintf.data:
            this_host = self.mgr.get(self.mgr.host_collection, name=self.hostintf.sysName)
            this_class = self.mgr.get(self.mgr.measurement_class_collection, name=data['class'], transport=data['transport'])
            this_inst = self.mgr.get_or_create(self.mgr.measurement_instance_collection,
                                               name=data['name'], index=data['index'],
                                               host=this_host,
                                               measurement_class=this_class)
            self.assertIsInstance(this_inst, dict)

    def test_manager_update_measurement_instance(self):
        for data in self.hostintf.data:
            this_inst = self.mgr.get(self.mgr.measurement_instance_collection, name=data['name'])
            this_inst = self.mgr.update(self.mgr.measurement_instance_collection, this_inst,
                                        name=data['name'],
                                        attrs=json_ready(data['attrs']),
                                        presentation=json_ready(data['presentation']),
                                        metrics=json_ready(data['metrics']))
            self.assertIsInstance(this_inst, dict)

    def test_manager_get_instances_by_presentation(self):
        x = self.mgr.get_instances_by_presentation("title", re.compile("%s.*" % self.hostintf.sysName))
        self.assertIsInstance(x, list)
        self.assertEquals(len(x), len(self.hostintf.data))
