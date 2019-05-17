# Written by Stephen Fromm <stephenf nero net>
# Copyright (C) 2016-2017 University of Oregon
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
import netspryte.snmp
import netspryte.utils
from netspryte.errors import NetspryteError


class HostSystem(object):

    NAME = 'system'
    DESCRIPTION = "Base System SNMP Information"
    ATTR_MODEL = "HostSnmpAttrs"

    ATTRS = {
        'sysdescr': '1.3.6.1.2.1.1.1',
        'sysobjectid': '1.3.6.1.2.1.1.2',
        'sysuptime': '1.3.6.1.2.1.1.3',
        'syscontact': '1.3.6.1.2.1.1.4',
        'sysname': '1.3.6.1.2.1.1.5',
        'syslocation': '1.3.6.1.2.1.1.6',
        'sysservices': '1.3.6.1.2.1.1.7',
    }

    STAT = {}

    XLATE = {}

    CONVERSION = {}

    def __init__(self, snmp):
        self._sysdescr = None
        self._sysobjectid = None
        self._sysuptime = None
        self._syscontact = None
        self._sysname = None
        self._syslocation = None
        self._sysservices = None
        self.snmp = snmp
        logging.info("inspecting %s for sys data", snmp.host)
        self.data = self._get_system()
        if not self.data:
            raise NetspryteError("failed to gather base snmp host information")
        for k, v in list(self.data[0]['attrs'].items()):
            setattr(self, k, v)
        logging.info("done inspecting %s for sys data", snmp.host)

    def _get_system(self):
        data = dict()
        attrs = netspryte.snmp.get_snmp_data(self.snmp, self, HostSystem.NAME, HostSystem.ATTRS, HostSystem.CONVERSION)
        for k, v in list(attrs.items()):
            host = None
            if 'sysname' in v:
                host = v['sysname']
            data[k] = self.initialize_instance(HostSystem.NAME, k, host)
            data[k]['attrs'] = v
        return data

    def initialize_instance(self, measurement_class, index, host=None):
        ''' return a dictionary with the basics of a measurement instance '''
        data = dict()
        data['host'] = self.sysname or self.snmp.host
        if host:
            data['host'] = host
        data['class'] = measurement_class
        data['index'] = index
        data['title'] = ""
        data['description'] = ""
        data['transport'] = 'snmp'
        if netspryte.utils.check_hash_snmp_index(index):
            index = netspryte.utils.mk_secure_hash(index)
        data['name'] = netspryte.utils.mk_data_instance_id(data['host'], measurement_class, index)
        return data

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, arg):
        if isinstance(arg, dict):
            self._data = list(arg.values())
        else:
            self._data = arg

    @property
    def sysdescr(self):
        return self._sysdescr

    @sysdescr.setter
    def sysdescr(self, arg):
        self._sysdescr = arg

    @property
    def sysobjectid(self):
        return self._sysobjectid

    @sysobjectid.setter
    def sysobjectid(self, arg):
        self._sysobjectid = arg

    @property
    def sysuptime(self):
        return self._sysuptime

    @sysuptime.setter
    def sysuptime(self, arg):
        self._sysuptime = arg

    @property
    def syscontact(self):
        return self._syscontact

    @syscontact.setter
    def syscontact(self, arg):
        self._syscontact = arg

    @property
    def sysname(self):
        return self._sysname

    @sysname.setter
    def sysname(self, arg):
        self._sysname = arg

    @property
    def syslocation(self):
        return self._syslocation

    @syslocation.setter
    def syslocation(self, arg):
        self._syslocation = arg

    @property
    def sysservices(self):
        return self._sysservices

    @sysservices.setter
    def sysservices(self, arg):
        self._sysservices = arg
