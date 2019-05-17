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
import binascii
from netspryte.snmp.host import HostSystem


class HostEntity(HostSystem):

    NAME = 'entity'
    DESCRIPTION = "Device Physical and Logical Components"

    ATTRS = {
        'entphysicaldescr': '1.3.6.1.2.1.47.1.1.1.1.2',
        'entphysicalvendortype': '1.3.6.1.2.1.47.1.1.1.1.3',
        'entphysicalcontainedin': '1.3.6.1.2.1.47.1.1.1.1.4',
        'entphysicalclass': '1.3.6.1.2.1.47.1.1.1.1.5',
        'entphysicalname': '1.3.6.1.2.1.47.1.1.1.1.7',
        'entphysicalhardwarerev': '1.3.6.1.2.1.47.1.1.1.1.8',
        'entphysicalfirmwarerev': '1.3.6.1.2.1.47.1.1.1.1.9',
        'entphysicalsoftwarerev': '1.3.6.1.2.1.47.1.1.1.1.10',
        'entphysicalserialnum': '1.3.6.1.2.1.47.1.1.1.1.11',
        'entphysicalmfgname': '1.3.6.1.2.1.47.1.1.1.1.12',
        'entphysicalmodelname': '1.3.6.1.2.1.47.1.1.1.1.13',
        'entphysicalassetid': '1.3.6.1.2.1.47.1.1.1.1.15',
        'entphysicalisfru': '1.3.6.1.2.1.47.1.1.1.1.16',
        'entphysicalmfgdate': '1.3.6.1.2.1.47.1.1.1.1.17',
    }

    STAT = {}

    CONVERSION = {
        'entPhysicalClass': {
            1: 'other',
            2: 'unknown',
            3: 'chassis',
            4: 'backplane',
            5: 'container',
            6: 'powerSupply',
            7: 'fan',
            8: 'sensor',
            9: 'module',
            10: 'port',
            11: 'stack',
            12: 'cpu',
        },
        'entPhysicalIsFRU': {
            1: 'true',
            2: 'false',
        },
    }

    def __init__(self, snmp):
        self.snmp = snmp
        super(HostEntity, self).__init__(snmp)
        self.data = self._get_configuration()

    def _get_configuration(self):
        data = dict()
        attrs = netspryte.snmp.get_snmp_data(self.snmp, self, HostEntity.NAME, HostEntity.ATTRS, HostEntity.CONVERSION)
        for k, v in list(attrs.items()):
            data[k] = self.initialize_instance(HostEntity.NAME, k)
            data[k]['attrs'] = v
            if 'entphysicalmfgdate' in v and v['entphysicalmfgdate']:
                data[k]['attrs']['entphysicalmfgdate'] = binascii.b2a_hex(v['entphysicalmfgdate'].encode('utf-8'))
        return data
