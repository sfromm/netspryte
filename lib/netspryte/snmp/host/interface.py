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
from netspryte.utils import *
from netspryte.utils.timer import Timer
from pysnmp.proto.rfc1902 import Counter32

class HostInterface(HostSystem):

    NAME = 'interface'
    DESCRIPTION = "Network Interfaces"

    ATTRS = {
        'ifIndex'       : '1.3.6.1.2.1.2.2.1.1',
        'ifDescr'       : '1.3.6.1.2.1.2.2.1.2',
        'ifType'        : '1.3.6.1.2.1.2.2.1.3',
        'ifMtu'         : '1.3.6.1.2.1.2.2.1.4',
        'ifSpeed'       : '1.3.6.1.2.1.2.2.1.5',
        'ifPhysAddress' : '1.3.6.1.2.1.2.2.1.6',
        'ifAdminStatus' : '1.3.6.1.2.1.2.2.1.7',
        'ifOperStatus'  : '1.3.6.1.2.1.2.2.1.8',
        'ifName'        : '1.3.6.1.2.1.31.1.1.1.1',
        'ifHighSpeed'   : '1.3.6.1.2.1.31.1.1.1.15',
        'ifAlias'       : '1.3.6.1.2.1.31.1.1.1.18',
    }

    STAT = {
        'ifInNUcastPkts'       : '1.3.6.1.2.1.2.2.1.12',
        'ifInDiscards'         : '1.3.6.1.2.1.2.2.1.13',
        'ifInErrors'           : '1.3.6.1.2.1.2.2.1.14',
        'ifInUnknownProtos'    : '1.3.6.1.2.1.2.2.1.15',
        'ifOutNUcastPkts'      : '1.3.6.1.2.1.2.2.1.18',
        'ifOutDiscards'        : '1.3.6.1.2.1.2.2.1.19',
        'ifOutErrors'          : '1.3.6.1.2.1.2.2.1.20',
        'ifOutQLen'            : '1.3.6.1.2.1.2.2.1.21',
        'ifInMulticastPkts'    : '1.3.6.1.2.1.31.1.1.1.2',
        'ifInBroadcastPkts'    : '1.3.6.1.2.1.31.1.1.1.3',
        'ifOutMulticastPkts'   : '1.3.6.1.2.1.31.1.1.1.4',
        'ifOutBroadcastPkts'   : '1.3.6.1.2.1.31.1.1.1.5',
        'ifHCInOctets'         : '1.3.6.1.2.1.31.1.1.1.6',
        'ifHCInUcastPkts'      : '1.3.6.1.2.1.31.1.1.1.7',
        'ifHCInMulticastPkts'  : '1.3.6.1.2.1.31.1.1.1.8',
        'ifHCInBroadcastPkts'  : '1.3.6.1.2.1.31.1.1.1.9',
        'ifHCOutOctets'        : '1.3.6.1.2.1.31.1.1.1.10',
        'ifHCOutUcastPkts'     : '1.3.6.1.2.1.31.1.1.1.11',
        'ifHCOutMulticastPkts' : '1.3.6.1.2.1.31.1.1.1.12',
        'ifHCOutBroadcastPkts' : '1.3.6.1.2.1.31.1.1.1.13',
    }

    XLATE = {
        'ifHC' : '',
        'if'   : '',
    }

    CONVERSION = {
        'ifAdminStatus': {
            1 : 'up',
            2 : 'down',
            3 : 'testing',
        },
        'ifOperStatus': {
            1 : 'up',
            2 : 'down',
            3 : 'testing',
            4 : 'unknown',
            5 : 'dormant',
            6 : 'notPresent',
            7 : 'lowerLayerDown',
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
        for k, v in attrs.iteritems():
            title = "{0}:{1}".format(self.sysName, attrs[k].get('ifDescr', 'NA'))
            descr = attrs[k].get('ifAlias', 'NA')
            data[k] = self.initialize_instance(HostInterface.NAME, k)
            data[k]['attrs'] = v
            if 'ifPhysAddress' in v and v['ifPhysAddress']:
                data[k]['attrs']['ifPhysAddress'] = ':'.join(['%x' % ord(x) for x in v['ifPhysAddress']])

            data[k]['presentation'] = {'title': title, 'description': descr}
            if k in metrics:
                data[k]['metrics'] = metrics[k]
                # In the event that not all STATs are returned
                # (eg not available or supported for a particular ifType),
                # go back and put them in the recorded metrics for this measurement
                # instance.  Fake a COUNTER value of 0.
                for stat in HostInterface.STAT.keys():
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
