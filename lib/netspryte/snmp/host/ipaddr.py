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
import ipaddress
from netspryte.snmp.host import HostSystem
from netspryte.snmp.host.interface import HostInterface
from netspryte.utils.timer import Timer


class HostIpAddress(HostSystem):

    NAME = 'ipaddress'
    DESCRIPTION = 'IP Address'
    ATTR_MODEL = "IPAddressAttrs"

    ATTRS = {
        'ipadentifindex': '1.3.6.1.2.1.4.20.1.2',  # ipAdEntIfIndex
        'netmask': '1.3.6.1.2.1.4.20.1.3',  # ipAdEntNetMask
        'addresstype': '1.3.6.1.2.1.4.34.1.1',  # ipAddressAddrType
        'ipaddress': '1.3.6.1.2.1.4.34.1.2',  # ipAddressAddr
        'ifindex': '1.3.6.1.2.1.4.34.1.3',  # ipAddressIfIndex
        'ipaddresstype': '1.3.6.1.2.1.4.34.1.4',  # ipAddressType
        'prefix': '1.3.6.1.2.1.4.34.1.5',  # ipAddressPrefix
        'origin': '1.3.6.1.2.1.4.34.1.6',  # ipAddressOrigin
        'status': '1.3.6.1.2.1.4.34.1.7',  # ipAddressStatus
    }

    STAT = {}

    XLATE = {}

    CONVERSION = {
        'addresstype': {
            0: 'unknown',
            1: 'ipv4',
            2: 'ipv6',
            3: 'ipv4z',
            4: 'ipv6z',
            16: 'dns',
        },
        'ipaddresstype': {
            1: 'unicast',
            2: 'anycast',
            3: 'broadcast',
        },
        'origin': {
            1: 'other',
            2: 'manual',
            4: 'dhcp',
            5: 'linklayer',
            6: 'random',
        },
        'status': {
            1: 'preferred',
            2: 'deprecated',
            3: 'invalid',
            4: 'inaccessible',
            5: 'unknown',
            6: 'tentative',
            7: 'duplicate',
            8: 'optimistic',
        },
    }

    def __init__(self, snmp):
        self.snmp = snmp
        super(HostIpAddress, self).__init__(snmp)
        t = Timer("snmp inspect %s %s" % (HostIpAddress.NAME, snmp.host))
        t.start_timer()
        self.data = self._get_configuration()
        t.stop_timer()

    def _get_configuration(self):
        data = dict()
        attrs = netspryte.snmp.get_snmp_data(self.snmp, self, HostIpAddress.NAME,
                                             HostIpAddress.ATTRS, HostIpAddress.CONVERSION)
        for k, v in list(attrs.items()):
            if 'ipadentifindex' in v:
                netmask = v['netmask']
                ifindex = v['ipadentifindex']
                net = ipaddress.ip_network('%s/%s' % (k, netmask), strict=False)
                data[k] = self.initialize_instance(HostInterface.NAME, ifindex)
                data[k]['attrs'] = dict()
                data[k]['attrs']['ipaddress'] = k
                data[k]['attrs']['prefix'] = net.prefixlen
                data[k]['attrs']['addresstype'] = 'ipv4'
                data[k]['attrs']['ifindex'] = ifindex

        for k, v in list(attrs.items()):
            if 'ipadentifindex' in v:
                continue
            if 'prefix' not in v:
                continue
            ifindex = v['ifindex']
            (addr_type, sub1, addr1) = k.split('.', 2)
            attrs[k]['addresstype'] = HostIpAddress.CONVERSION['addresstype'][int(addr_type)]
            addr2 = ""
            if attrs[k]['addresstype'] == 'ipv4':
                addr2 = addr1
            if attrs[k]['addresstype'] == 'ipv6':
                addrt = addr1.split(".")
                for j, val in enumerate(addrt):
                    addrt[j] = hex(int(val))[2:].zfill(2)
                t = iter(addrt)
                addr2 = ':'.join([i + next(t, '') for i in t])

            data[addr2] = self.initialize_instance(HostInterface.NAME, ifindex)
            data[addr2]['attrs'] = v
            data[addr2]['attrs']['ipaddress'] = addr2
            data[addr2]['attrs']['prefix'] = str(attrs[k]['prefix']).split(".")[-1]
        return data
