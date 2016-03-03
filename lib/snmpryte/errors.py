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

class SnmpryteError(Exception):
    '''
    A base class for all errors from Mopticon code.
    Usage:

        raise SnmpryteError('error message')
    '''

    def __init__(self, message):
        self.message = 'ERROR! %s' % message

    def __str__(self):
        return self.message

    def __repr__(self):
        return self.message

class SnmpryteSNMPError(SnmpryteError):
    pass
