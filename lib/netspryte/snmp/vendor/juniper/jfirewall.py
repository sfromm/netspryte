# Written by Stephen Fromm <stephenf nero net>
# Copyright (C) 2019 University of Oregon
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
import netspryte.snmp.host.interface
from netspryte.snmp.vendor.juniper import JuniperDevice
from netspryte.utils import mk_data_instance_id
from netspryte.utils.timer import Timer


class JFirewall(JuniperDevice):

    NAME = 'jfirewall'
    DESCRIPTION = "Juniper Firewall"
    ATTR_MODEL = "QOSAttrs"
    METRIC_MODEL = "QOSMetrics"

    ATTRS = {
        'countertype': '1.3.6.1.4.1.2636.3.5.2.1.3',  # jnxFWCounterType
        'policymapname': '1.3.6.1.4.1.2636.3.5.2.1.7',  # jnxFWCounterDisplayName
        'objectstype': '1.3.6.1.4.1.2636.3.5.2.1.8',  # jnxFWCounterDisplayType
    }

    STAT = {
        'postpolicypkts': '1.3.6.1.4.1.2636.3.5.2.1.4',  # jnxFWCounterPacketCount
        'postpolicybyte': '1.3.6.1.4.1.2636.3.5.2.1.5',  # jnxFWCounterByteCount
    }

    CONVERSION = {
        'objectstype': {
            1: 'other',
            2: 'counter',
            3: 'policer',
            4: 'hpolagg',
            5: 'hpolpre',
        },
        'jnxFWCounterDisplayType': {
            1: 'other',
            2: 'counter',
            3: 'policer',
            4: 'hpolagg',
            5: 'hpolpre',
        },
    }

    XLATE = {
        'Counter': '',
        'jnxFW': 'fw',
        'Count': '',
    }

    SNMP_QUERY_CHUNKS = 1

    def __init__(self, snmp):
        self.snmp = snmp
        self.data = dict()
        t = Timer("snmp inspect %s %s" % (JFirewall.NAME, snmp.host))
        t.start_timer()
        super(JFirewall, self).__init__(snmp)
        if JuniperDevice.BASE_OID not in str(self.sysobjectid):
            logging.debug("skipping firweall check on non-juniper device %s", self.sysname)
            return
        logging.info("inspecting %s for firewall data", snmp.host)
        host = netspryte.snmp.host.interface.HostInterface(self.snmp)
        self.interfaces = host.interfaces
        self.data = self._get_configuration()
        t.stop_timer()

    def _get_configuration(self):
        ''' get junos firewall objects '''
        data = dict()
        attrs = netspryte.snmp.get_snmp_data(self.snmp, self, JFirewall.NAME,
                                             JFirewall.ATTRS, JFirewall.CONVERSION)
        metrics = netspryte.snmp.get_snmp_data(self.snmp, self, JFirewall.NAME,
                                               JFirewall.STAT, JFirewall.CONVERSION)
        for k, v in list(attrs.items()):
            title = attrs[k].get('policymapname', 'NA')
            descr = "{0}: {1}".format(title, attrs[k].get('displaytype', 'NA'))
            policydirection = ""
            # This module will only focus on those firewall filters applied to interfaces.
            # These filters will have a "-i" or "-o" suffix that indicates direction that it is applied.
            # Example: accept-bfd-lo0.0-i
            if title.endswith('-i'):
                policydirection = 'input'
            elif title.endswith('-o'):
                policydirection = 'output'
            else:
                continue
            # Extract interface name from firewall filter name.
            # This is the component before the direction indicator.
            # Example: accept-bfd-lo0.0-i
            ifname = title.split('-')[-2]
            ifindex = None
            for intf in self.interfaces:
                if intf['attrs']['ifname'] == ifname:
                    ifindex = intf['attrs']['ifindex']
            if not ifindex:
                continue
            # The normal convention is to use the index when initializing the instance.
            # because the snmp table index for this mib is unbelievably long, I need to use something else.
            # i've opted to use the title variable.
            data[k] = self.initialize_instance(JFirewall.NAME, k)
            data[k]['attrs'] = v
            data[k]['attrs']['ifindex'] = ifindex
            data[k]['attrs']['policydirection'] = policydirection
            data[k]['title'] = title
            data[k]['description'] = descr
            if k in metrics:
                data[k]['metrics'] = metrics[k]

            if 'related' not in data[k]:
                data[k]['related'] = dict()
            data[k]['related']['metric_model'] = netspryte.snmp.host.interface.HostInterface.METRIC_MODEL
            data[k]['related']['name'] = mk_data_instance_id(data[k]['host'],
                                                             netspryte.snmp.host.interface.HostInterface.NAME,
                                                             ifindex)
        return data
