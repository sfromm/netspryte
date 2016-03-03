# Written by Stephen Fromm <stephenf nero net>
# (C) 2015 University of Oregon

# This file is part of snmpryte
#
# snmpryte is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# snmpryte is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with snmpryte.  If not, see <http://www.gnu.org/licenses/>.

import snmpryte
import snmpryte.snmp
from snmpryte import constants as C
from snmpryte.errors import *

class Device(object):

    def __init__(self, snmp=None):
        if snmp:
            self.snmp = snmp

    @property
    def snmp(self):
        return self._snmp

    @snmp.setter
    def snmp(self, arg):
        if isinstance(arg, MSnmp):
            self._snmp = arg
        else:
            raise ValueError("SNMP argument must be a MSnmp object")
