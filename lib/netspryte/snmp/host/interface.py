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
from netspryte.utils.timer import Timer
from pysnmp.proto.rfc1902 import Counter32


class HostInterface(HostSystem):

    NAME = 'interface'
    DESCRIPTION = "Network Interfaces"
    ATTR_MODEL = "InterfaceAttrs"
    METRIC_MODEL = "InterfaceMetrics"

    ATTRS = {
        'ifindex': '1.3.6.1.2.1.2.2.1.1',
        'ifdescr': '1.3.6.1.2.1.2.2.1.2',
        'iftype': '1.3.6.1.2.1.2.2.1.3',
        'ifmtu': '1.3.6.1.2.1.2.2.1.4',
        'ifspeed': '1.3.6.1.2.1.2.2.1.5',
        'ifphysaddress': '1.3.6.1.2.1.2.2.1.6',
        'ifadminstatus': '1.3.6.1.2.1.2.2.1.7',
        'ifoperstatus': '1.3.6.1.2.1.2.2.1.8',
        'ifname': '1.3.6.1.2.1.31.1.1.1.1',
        'ifhighspeed': '1.3.6.1.2.1.31.1.1.1.15',
        'ifalias': '1.3.6.1.2.1.31.1.1.1.18',
    }

    STAT = {
        'innucastpkts': '1.3.6.1.2.1.2.2.1.12',
        'indiscards': '1.3.6.1.2.1.2.2.1.13',
        'inerrors': '1.3.6.1.2.1.2.2.1.14',
        'inunknownprotos': '1.3.6.1.2.1.2.2.1.15',
        'outnucastpkts': '1.3.6.1.2.1.2.2.1.18',
        'outdiscards': '1.3.6.1.2.1.2.2.1.19',
        'outerrors': '1.3.6.1.2.1.2.2.1.20',
        'outqlen': '1.3.6.1.2.1.2.2.1.21',
        'inoctets': '1.3.6.1.2.1.31.1.1.1.6',   # ifHCInOctets
        'inucastpkts': '1.3.6.1.2.1.31.1.1.1.7',   # ifHCInUcastPkts
        'inmulticastpkts': '1.3.6.1.2.1.31.1.1.1.8',   # ifHCInMulticastPkts
        'inbroadcastpkts': '1.3.6.1.2.1.31.1.1.1.9',   # ifHCInBroadcastPkts
        'outoctets': '1.3.6.1.2.1.31.1.1.1.10',  # ifHCOutOctets
        'outucastpkts': '1.3.6.1.2.1.31.1.1.1.11',  # ifHCOutUcastPkts
        'outmulticastpkts': '1.3.6.1.2.1.31.1.1.1.12',  # ifHCOutMulticastPkts
        'outbroadcastpkts': '1.3.6.1.2.1.31.1.1.1.13',  # ifHCOutBroadcastPkts
    }

    XLATE = {
        'ifHC': '',
        'if': '',
    }

    CONVERSION = {
        'ifadminstatus': {
            1: 'up',
            2: 'down',
            3: 'testing',
        },
        'ifoperstatus': {
            1: 'up',
            2: 'down',
            3: 'testing',
            4: 'unknown',
            5: 'dormant',
            6: 'notPresent',
            7: 'lowerLayerDown',
        },
    }

    def __init__(self, snmp):
        self.snmp = snmp
        super(HostInterface, self).__init__(snmp)
        t = Timer("snmp inspect %s %s" % (HostInterface.NAME, snmp.host))
        t.start_timer()
        self.data = self._get_interface()
        t.stop_timer()

    def _get_interface(self):
        '''
        Pull together attributes and metrics for all interfaces into a dictionary
        associated with with a SNMP object for a device.
        '''
        data = dict()
        attrs = netspryte.snmp.get_snmp_data(self.snmp, self, HostInterface.NAME, HostInterface.ATTRS, HostInterface.CONVERSION)
        metrics = netspryte.snmp.get_snmp_data(self.snmp, self, HostInterface.NAME, HostInterface.STAT, HostInterface.CONVERSION)
        for k, v in list(attrs.items()):
            ifdescr = attrs[k].get('ifdescr', 'NA')
            title = "{0}:{1}".format(self.sysname, ifdescr)
            descr = attrs[k].get('ifalias', ifdescr)
            data[k] = self.initialize_instance(HostInterface.NAME, k)
            data[k]['attrs'] = v
            if 'ifphysaddress' in v and v['ifphysaddress']:
                data[k]['attrs']['ifphysaddress'] = ':'.join(['%x' % ord(x) for x in v['ifphysaddress']])
            data[k]['title'] = title
            data[k]['description'] = descr
            if k in metrics:
                data[k]['metrics'] = metrics[k]
                # In the event that not all STATs are returned
                # (eg not available or supported for a particular ifType),
                # go back and put them in the recorded metrics for this measurement
                # instance.  Fake a COUNTER value of 0.
                for stat in list(HostInterface.STAT.keys()):
                    if stat not in data[k]['metrics']:
                        data[k]['metrics'][stat] = Counter32(0)
        return data

    @property
    def interfaces(self):
        return self.data

    @property
    def stat(self):
        return self._data

    def get_interface_stats(self):
        return netspryte.snmp.get_snmp_data(self.snmp, self, HostInterface.NAME,
                                            HostInterface.STAT, HostInterface.CONVERSION)
