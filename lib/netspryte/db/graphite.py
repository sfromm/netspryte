# Written by Stephen Fromm <stephenf nero net>
# Copyright (C) 2018 University of Oregon
#
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

import logging
import socket
import time
import urllib.request

from netspryte.db import BaseDatabaseBackend
import netspryte.snmp
from netspryte import constants as C


class GraphiteDatabaseBackend(BaseDatabaseBackend):

    def __init__(self, backend, **kwargs):
        super(GraphiteDatabaseBackend, self).__init__(backend, **kwargs)
        self.host = kwargs.get('host', C.DEFAULT_CARBON_HOST)
        self.port = kwargs.get('port', C.DEFAULT_CARBON_PORT)
        self.measurement_instance = None
        self.sock = socket.socket()
        self.sock.connect((self.host, self.port))

    @property
    def host(self):
        return self._host

    @host.setter
    def host(self, arg):
        self._host = arg

    @property
    def port(self):
        return self._port

    @port.setter
    def port(self, arg):
        try:
            self._port = int(arg)
        except ValueError:
            raise ValueError("Graphite port must be an integer")

    def write(self, data, xlate, ts=time.time()):
        ''' send data to graphite server '''
        if self.measurement_instance is None:
            logging.error("unable to write to graphite without a measurement_instance property")
            return None
        msgs = list()
        ts = int(ts)
        mcls_name = self.measurement_instance.measurement_class.name
        mcls_transport = self.measurement_instance.measurement_class.transport
        name = self.measurement_instance.name
        index = self.measurement_instance.index
        host = self.measurement_instance.host.name
        tags = "host={0};measurement_class={1};transport={2};name={3};index={4}".format(
            host, mcls_name, mcls_transport, name, index
        )
        for k, v in list(self.measurement_instance.attrs):
            tags += ";{0}={1}".format(k.lower(), v)
        for k, v in list(data.items()):
            msg = "{0}.{1};{2} {3} {4}".format(
                mcls_name, k, tags, v, ts
            )
            msgs.append(msg)
        self.sock.sendall("\n".join(msgs))

    def graph(self, xargs):
        ''' build request and return a graph object from graphite '''
        url = "http://{0}:{1}/render?".format(C.DEFAULT_GRAPHITE_HOST,
                                              C.DEFAULT_GRAPHITE_PORT)
        for k, v in list(xargs.items()):
            url += "{0}={1}".format(k, v)
        graph = None
        with urllib.request.urlopen(url) as g:
            graph = g.read()
        return graph
