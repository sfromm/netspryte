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

    ATTRS = {
        'sysDescr'    : '1.3.6.1.2.1.1.1',
        'sysObjectID' : '1.3.6.1.2.1.1.2',
        'sysUpTime'   : '1.3.6.1.2.1.1.3',
        'sysContact'  : '1.3.6.1.2.1.1.4',
        'sysName'     : '1.3.6.1.2.1.1.5',
        'sysLocation' : '1.3.6.1.2.1.1.6',
        'sysServices' : '1.3.6.1.2.1.1.7',
    }

    STAT = { }

    XLATE = { }

    CONVERSION = { }

    def __init__(self, snmp):
        self._sysDescr    = None
        self._sysObjectID = None
        self._sysUpTime   = None
        self._sysContact  = None
        self._sysName     = None
        self._sysLocation = None
        self._sysServices = None
        self.snmp         = snmp
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
            if 'sysName' in v:
                host = v['sysName']
            data[k] = self.initialize_instance(HostSystem.NAME, k, host)
            data[k]['attrs'] = v
        return data

    def initialize_instance(self, measurement_class, index, host=None):
        ''' return a dictionary with the basics of a measurement instance '''
        data = dict()
        data['host'] = self.sysName or self.snmp.host
        if host:
            data['host'] = host
        data['class'] = measurement_class
        data['index'] = index
        data['transport'] = 'snmp'
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
    def sysDescr(self):
        return self._sysDescr

    @sysDescr.setter
    def sysDescr(self, arg):
        self._sysDescr = arg

    @property
    def sysObjectID(self):
        return self._sysObjectID

    @sysObjectID.setter
    def sysObjectID(self, arg):
        self._sysObjectID = arg

    @property
    def sysUpTime(self):
        return self._sysUpTime

    @sysUpTime.setter
    def sysUpTime(self, arg):
        self._sysUpTime = arg

    @property
    def sysContact(self):
        return self._sysContact

    @sysContact.setter
    def sysContact(self, arg):
        self._sysContact = arg

    @property
    def sysName(self):
        return self._sysName

    @sysName.setter
    def sysName(self, arg):
        self._sysName = arg

    @property
    def sysLocation(self):
        return self._sysLocation

    @sysLocation.setter
    def sysLocation(self, arg):
        self._sysLocation = arg

    @property
    def sysServices(self):
        return self._sysServices

    @sysServices.setter
    def sysServices(self, arg):
        self._sysServices = arg
