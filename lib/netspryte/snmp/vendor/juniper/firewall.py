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
from netspryte.utils.timer import Timer


class JuniperFirewall(JuniperDevice):

    NAME = 'juniperfirewall'
    DESCRIPTION = "Juniper Firewall"
    ATTR_MODEL = "JuniperFirewallAttrs"
    METRIC_MODEL = "JuniperFirewallMetrics"

    ATTRS = {
        'jnxFWCounterType': '1.3.6.1.4.1.2636.3.5.2.1.3',
        'jnxFWCounterDisplayName': '1.3.6.1.4.1.2636.3.5.2.1.7',
        'jnxFWCounterDisplayType': '1.3.6.1.4.1.2636.3.5.2.1.8',
    }

    STAT = {
        'jnxFWCounterPacketCount': '1.3.6.1.4.1.2636.3.5.2.1.4',
        'jnxFWCounterByteCount': '1.3.6.1.4.1.2636.3.5.2.1.5',
    }

    CONVERSION = {
        'jnxFWCounterType': {
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
        'Counter': 'cntr',
        'jnxFW': '',
    }

    SNMP_QUERY_CHUNKS = 1

    def __init__(self, snmp):
        self.snmp = snmp
        self.data = dict()
        t = Timer("snmp inspect %s %s" % (JuniperFirewall.NAME, snmp.host))
        t.start_timer()
        super(JuniperFirewall, self).__init__(snmp)
        if JuniperDevice.BASE_OID not in str(self.sysObjectID):
            logging.debug("skipping firweall check on non-juniper device %s", self.sysName)
            return None
        logging.info("inspecting %s for firewall data", snmp.host)
        host = netspryte.snmp.host.interface.HostInterface(self.snmp)
        self.interfaces = host.interfaces
        self.data = self._get_configuration()
        t.stop_timer()

    def _get_configuration(self):
        ''' get junos firewall objects '''
        data = dict()
        attrs = netspryte.snmp.get_snmp_data(self.snmp, self, JuniperFirewall.NAME,
                                             JuniperFirewall.ATTRS, JuniperFirewall.CONVERSION)
        metrics = netspryte.snmp.get_snmp_data(self.snmp, self, JuniperFirewall.NAME,
                                               JuniperFirewall.STAT, JuniperFirewall.CONVERSION)
        for k, v in list(attrs.items()):
            title = attrs[k].get('jnxCounterDisplayName', 'NA')
            descr = "{0}: {1}".format(title, attrs[k].get('jnxFWCounterDisplayType', 'NA'))
            data[k] = self.initialize_instance(JuniperFirewall.NAME, k)
            data[k]['attrs'] = v
            data[k]['title'] = title
            data[k]['description'] = descr
            if k in metrics:
                data[k]['metrics'] = metrics[k]
        return data
