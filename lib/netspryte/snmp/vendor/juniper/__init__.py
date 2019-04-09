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

from netspryte.snmp.host import HostSystem


class JuniperDevice(HostSystem):

    NAME = "juniper"
    DESCRIPTION = "Base Juniper Information"
    ATTR_MODEL = ""
    ATTRS = { }
    STAT = { }
    CONVERSION = { }
    XLATE = { }
    BASE_OID = "1.3.6.1.4.1.2636"

    def __init__(self, snmp):
        self.snmp = snmp
        super(JuniperDevice, self).__init__(snmp)
        self.data = dict()
