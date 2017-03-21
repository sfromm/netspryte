# Written by Stephen Fromm <stephenf nero net>
# Copyright (C) 2015-2017 University of Oregon

# This file is part of netspryte
#
# netspryte is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# netspryte is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with netspryte.  If not, see <http://www.gnu.org/licenses/>.

class NetspryteError(Exception):
    '''
    A base class for all errors from netspryte code.
    Usage:

        raise NetspryteError('error message')
    '''

    def __init__(self, message):
        self.message = 'ERROR! %s' % message

    def __str__(self):
        return self.message

    def __repr__(self):
        return self.message

class NetspryteSNMPError(NetspryteError):
    pass
