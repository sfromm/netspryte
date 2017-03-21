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

class BaseDatabaseBackend(object):

    def __init__(self, backend, **kwargs):
        ''' base backend for a database '''
        self.backend = backend
        if 'host' in kwargs:
            self.host = kwargs['host']

    def write(self, data):
        pass

    @property
    def backend(self):
        return self._backend

    @backend.setter
    def backend(self, arg):
        self._backend = arg

    @property
    def host(self):
        return self._host

    @host.setter
    def host(self, arg):
        self._host = arg
