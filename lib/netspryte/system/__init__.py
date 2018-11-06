# Written by Stephen Fromm <stephenf nero net>
# Copyright (C) 2015-2017 University of Oregon
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
import subprocess
import netspryte.constants as C
from netspryte.utils import parse_json


class SystemSession(object):

    NAME = "system"
    DESCRIPTION = "Base System Information Collector"

    def __init__(self, config):
        self.config = config
        self.host = socket.getfqdn()
        self.data = dict()
        self.transport = 'system'

    def run_process(self, args):
        ''' Run process and return return-code, stdout, and stderr '''
        proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        try:
            out, err = proc.communicate(timeout=C.DEFAULT_SYSTEM_TIMEOUT)
        except subprocess.TimeoutExpired:
            proc.kill()
            out, err = proc.communicate()
        rc = proc.returncode
        if rc != 0:
            logging.warn("system exec command %s returned non-zero: %s", args, rc)
        return (rc, out, err)

    def parse_process_output(output, fmt):
        ''' Parse process output according to supplied requested format '''
        data = output
        if not fmt:
            return data
        if fmt == 'json':
            data = parse_json(output)
        return data

    def initialize_instance(self, measurement_class, index, host=None):
        ''' return a dictionary with the basics of a measurement instance '''
        data = dict()
        data['host'] = self.host
        if host:
            data['host'] = host
        data['class'] = measurement_class
        data['index'] = index
        data['transport'] = self.transport
        data['name'] = netspryte.utils.mk_data_instance_id(data['host'], measurement_class, index)
        return data
