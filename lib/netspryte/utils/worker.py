# Written by Stephen Fromm <stephenf nero net>
# Copyright Copyright (C) 2018 University of Oregon
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.

import logging
import datetime
import multiprocessing
import netspryte
import netspryte.snmp
import peewee
from netspryte.snmp.host import HostSystem

import netspryte.model
from netspryte.utils import json_ready
from netspryte.utils.timer import Timer


class DataWorker(multiprocessing.Process):

    def __init__(self, task_queue):
        multiprocessing.Process.__init__(self)
        self.task_queue = task_queue

    # modules that inherit this must implement
    # def run(self):

    def process_module_data(self, data_mod):
        this_host = None
        this_class = None
        log_me = False
        has_metrics = list()
        metric_types = dict()
        if not data_mod.data:
            return
        t = Timer("database")
        t.start_timer()
        for data in data_mod.data:
            now = datetime.datetime.now()
            if not this_host:
                this_host = self.mgr.get_or_create(netspryte.model.Host, name=data['host'])
                self.process_host_attrs(data_mod, this_host)
            if not this_class:
                this_class = self.mgr.get_or_create(netspryte.model.MeasurementClass, name=data['class'], transport=data['transport'])
            if this_host is None or this_class is None:
                logging.error("encountered database error; skipping to next instance")
                continue
            t.name = "select and update database %s-%s" % (this_host.name, this_class.name)
            if not log_me:
                logging.info("updating database for %s %s", this_host.name, this_class.name)
                log_me = True
            if hasattr(data_mod, 'DESCRIPTION') and not this_class.description:
                this_class.description = data_mod.DESCRIPTION
            this_inst = self.mgr.get_or_create(netspryte.model.MeasurementInstance,
                                               name=data['name'], index=data['index'],
                                               host=this_host, measurement_class=this_class)
            this_inst.lastseen = now
            # populate presentation info
            if 'presentation' in data and not this_inst.presentation:
                this_inst.presentation = json_ready(data['presentation'])
            # prepare metrics for
            if 'metrics' in data:
                this_inst.metrics = json_ready(data['metrics'])
                if not metric_types:
                    for k, v in list(data['metrics'].items()):
                        metric_types[k] = netspryte.snmp.get_value_type(v)
                    this_class.metric_type = json_ready(metric_types)
            self.mgr.save(this_inst)
            self.process_data_instance_attrs(data, this_inst, data_mod.ATTR_MODEL)
            if this_inst.metrics:
                has_metrics.append(this_inst)
        self.mgr.save(this_host)
        self.mgr.save(this_class)
        logging.info("done updating database for %s %s", this_host.name, this_class.name)
        t.stop_timer()
        return has_metrics

    def process_data_instance_attrs(self, data, measurement_instance, model):
        ''' Process measurement instance attributes '''
        logging.debug("adding/updating attributes for %s", measurement_instance.name)
        init_attrs = dict()
        attrs = json_ready(data['attrs'])
        attrs['measurement_instance'] = measurement_instance
        if not hasattr(netspryte.model, model):
            logging.error("cannot find class model for %s attributes", measurement_instance.measurement_class.name)
            return None
        cls = getattr(netspryte.model, model)
        # This is probably supposed to be handled by process_host_attrs()
        if not hasattr(cls, 'measurement_instance'):
            logging.info("skipping model %s that does not have relation to measurement_instance", model)
            return
        for field in cls._meta.sorted_fields:
            if field.name == 'id' or isinstance(field, peewee.ForeignKeyField) or field.name not in attrs:
                continue
            if not field.null:
                init_attrs[field.name] = attrs[field.name]
        init_attrs['measurement_instance'] = measurement_instance
        m = self.mgr.get_or_create(cls, **init_attrs)
        if m is None:
            logging.error("failed to get or create attributes for measurement instance %s", measurement_instance)
            return None
        self.mgr.update(m, **attrs)
        return m

    def process_host_attrs(self, data, host):
        '''
        Process host snmp attributes
        data is a snmp module object
        host is a Host object
        '''
        attrs = dict()
        for attr in HostSystem.ATTRS.keys():
            if hasattr(data, attr):
                attrs[attr] = getattr(data, attr)
        attrs = json_ready(attrs)
        attrs['host'] = host
        cls = getattr(netspryte.model, HostSystem.ATTR_MODEL)
        m = self.mgr.get_or_create(cls, sysName=attrs['sysName'], sysObjectID=attrs['sysObjectID'], host=host)
        if m is None:
            logging.error("failed to get or create attributes for host %s", host.name)
            return None
        self.mgr.update(m, **attrs)
        return m
