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
from netspryte.snmp.host import HostSystem


class HostIpNetwork(HostSystem):

    NAME = 'ipnetwork'
    DESCRIPTION = 'IP Networks'

    ATTRS = {
#        'ipAddressPrefixOrigin' : '1.3.6.1.2.1.4.32.1.5',
        'ipAddressAddrType'     : '1.3.6.1.2.1.4.34.1.1',
        'ipAddressAddr'         : '1.3.6.1.2.1.4.34.1.2',
        'ipAddressIfIndex'      : '1.3.6.1.2.1.4.34.1.3',
        'ipAddressType'         : '1.3.6.1.2.1.4.34.1.4',
        'ipAddressPrefix'       : '1.3.6.1.2.1.4.34.1.5',
        'ipAddressOrigin'       : '1.3.6.1.2.1.4.34.1.6',
        'ipAddressStatus'       : '1.3.6.1.2.1.4.34.1.7',
        'ipAddressCreated'      : '1.3.6.1.2.1.4.34.1.8',
        'ipAddressLastChanged'  : '1.3.6.1.2.1.4.34.1.9',
    }

    STAT = { }

    XLATE = { }

    CONVERSION = {
        'ipAddressAddrType' : {
            0 : 'unknown',
            1 : 'ipv4',
            2 : 'ipv6',
            3 : 'ipv4z',
            4 : 'ipv6z',
            16 : 'dns',
        },
        'ipAddressType' : {
            1 : 'unicast',
            2 : 'anycast',
            3 : 'broadcast',
        },
        'ipAddressOrigin' : {
            1 : 'other',
            2 : 'manual',
            4 : 'dhcp',
            5 : 'linklayer',
            6 : 'random',
        },
        'ipAddressStatus' : {
            1 : 'preferred',
            2 : 'deprecated',
            3 : 'invalid',
            4 : 'inaccessible',
            5 : 'unknown',
            6 : 'tentative',
            7 : 'duplicate',
            8 : 'optimistic',
        },
        'ipAddressPrefixOrigin' : {
            1 : 'other',
            2 : 'manual',
            3 : 'wellknown',
            4 : 'dhcp',
            5 : 'routeradv',
        },
    }

    def __init__(self, snmp):
        self.snmp = snmp
        super(HostIpNetwork, self).__init__(snmp)
        logging.info("inspecting %s for ip address data", snmp.host)
        self.data = self._get_data()

    def _get_data(self):
        data = dict()
        attrs = netspryte.snmp.get_snmp_data(self.snmp, self, HostIpNetwork.NAME,
                                             HostIpNetwork.ATTRS, HostIpNetwork.CONVERSION)
        for k, v in list(attrs.items()):
            data[k] = self.initialize_instance(HostIpNetwork.NAME, k)
            data[k]['attrs'] = v
            (addr_type, sub1, addr1) = k.split('.', 2)
            attrs[k]['ipAddressAddrType'] = HostIpNetwork.CONVERSION['ipAddressAddrType'][int(addr_type)]
            addr2 = ""
            if attrs[k]['ipAddressAddrType'] == 'ipv4':
                addr2 = addr1
            if attrs[k]['ipAddressAddrType'] == 'ipv6':
                addr2 = ""
                for n in addr1.split('.'):
                    addr2 += format(int(n), 'x') + ":"
                addr2 = addr2[0:-1]
            data[k]['attrs']['ipAddressAddr'] = addr2
            data[k]['attrs']['ipAddressPrefix'] = str(attrs[k]['ipAddressPrefix']).split(".")[-1]
        return data
