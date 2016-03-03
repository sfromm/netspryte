# Written by Stephen Fromm <stephenf nero net>
# (C) 2016 University of Oregon
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
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
import snmpryte.snmp

class HostInterface():

    CONF = {
        'ifIndex'       : '1.3.6.1.2.1.2.2.1.1',
        'ifDescr'       : '1.3.6.1.2.1.2.2.1.2',
        'ifType'        : '1.3.6.1.2.1.2.2.1.3',
        'ifMtu'         : '1.3.6.1.2.1.2.2.1.4',
        'ifSpeed'       : '1.3.6.1.2.1.2.2.1.5',
        'ifPhysAddress' : '.1.3.6.1.2.1.2.2.1.6',
        'ifAdminStatus' : '1.3.6.1.2.1.2.2.1.7',
        'ifOperStatus'  : '1.3.6.1.2.1.2.2.1.8',
        'ifName'        : '1.3.6.1.2.1.31.1.1.1.1',
        'ifHighSpeed'   : '1.3.6.1.2.1.31.1.1.1.15',
        'ifAlias'       : '1.3.6.1.2.1.31.1.1.1.18',
    }

    STAT = {
        'ifInUcastPkts'     : '1.3.6.1.2.1.2.2.1.11',
        'ifInNUcastPkts'    : '1.3.6.1.2.1.2.2.1.12',
        'ifInDiscards'      : '1.3.6.1.2.1.2.2.1.13',
        'ifInErrors'        : '1.3.6.1.2.1.2.2.1.14',
        'ifInUnknownProtos' : '1.3.6.1.2.1.2.2.1.15',
        'ifOutUcastPkts'    : '1.3.6.1.2.1.2.2.1.17',
        'ifOutNUcastPkts'   : '1.3.6.1.2.1.2.2.1.18',
        'ifOutDiscards'     : '1.3.6.1.2.1.2.2.1.19',
        'ifOutErrors'       : '1.3.6.1.2.1.2.2.1.20',
        'ifOutQLen'         : '1.3.6.1.2.1.2.2.1.21',
    }

    CONVERSION = { }

    def __init__(self, snmp):
        self.snmp = snmp
        self._interfaces = self._get_configuration()

    def _get_configuration(self):
        return snmpryte.snmp.get_snmp_data(self.snmp, HostInterface.CONF, HostInterface.CONVERSION)

    @property
    def interfaces(self):
        return self._interfaces

    def get_interface_stats(self):
        pass
