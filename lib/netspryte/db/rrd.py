# Written by Stephen Fromm <stephenf nero net>
# (C) 2016 University of Oregon
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

import os
import logging
import rrdtool
import time
import subprocess

from netspryte.db import *
import netspryte.snmp
from netspryte import constants as C

class RrdDatabaseBackend(BaseDatabaseBackend):

    def __init__(self, backend, **kwargs):
        super(RrdDatabaseBackend, self).__init__(backend, **kwargs)
        if 'path' in kwargs:
            self._path = kwargs['path']

    def write(self, data):
        ''' write data to rrd database '''
        if not os.path.exists(self.path):
            rrd_create(self.path, C.DEFAULT_RRD_STEP, data, C.DEFAULT_RRD_RRA)
        return rrd_update(self.path, data)

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, arg):
        self._path = arg

def rrd_create(path, step, data, rra):
    ''' create a rrd '''
    args = [path, '--step', str(step)]
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    try:
        data_sources = mk_rrd_ds(data)
        logging.debug("RRD STEP: %s", step)
        logging.debug("RRD DS: %s", " ".join(data_sources))
        logging.debug("RRD RRA: %s", " ".join(rra))
        logging.info("creating rrd %s", path)
        rrdtool.create(str(path), '--step', str(step), data_sources, *rra)
    except rrdtool.error as e:
        logging.error("failed to create rrd %s: %s", path, str(e))

def rrd_update(path, data, ts=time.time()):
    ''' update rrd '''
    template = list()
    values = list()
    for k, v in data.iteritems():
        template.append(k.lower())
        if hasattr(v, 'prettyPrint'):
            values.append(v.prettyPrint())
        else:
            values.append(str(v))
        flat_template = ":".join(template)
    flat_values = ":".join(values)
    try:
        logging.info("updating rrd %s", path)
        rrdtool.update(str(path), '--template', flat_template, "%s:%s" % (ts, flat_values))
    except rrdtool.error as e:
        logging.error("failed to update rrd %s: %s", path, str(e))

def rrd_graph(path, rrd_opts, graph_opts):
    ''' create a graph for rrd '''
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    try:
        logging.info("creating graph %s", path)
        rrdtool.graph(path, rrd_opts, graph_opts)
    except rrdtool.error as e:
        logging.error("failed to create graph %s: %s", path, str(e))

def rrd_dump(path):
    ''' dump rrd to xml string '''
    try:
        logging.info("dumping xml %s", path)
        cmd = ['rrdtool', 'dump', path]
        popen = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        stdout = iter(popen.stdout.readline, "")
        for line in stdout:
            yield line
        popen.stdout.close()
        rc = popen.wait()
    except Exception as e:
        logging.error("failed to dump rrd %s to xml: %s", path, str(e))

def rrd_restore(xml_path, rrd_path):
    ''' restore rrd from xml file '''
    cmd = ['rrdtool', 'restore', xml_path, rrd_path]
    popen = subprocess.Popen(cmd, stdout=subprocess.PIPE)

def rrd_info(path):
    try:
        logging.debug("getting info for rrd %s", path)
        return rrdtool.info(path)
    except rrdtool.error as e:
        logging.error("failed to get info for %s: %s", path, str(e))

def mk_rrd_ds(data):
    ''' take in dictionary of collected values and return a list of DS '''
    ds = list()
    heartbeat = C.DEFAULT_RRD_STEP * C.DEFAULT_RRD_HEARTBEAT
    for k, v in data.iteritems():
        type = netspryte.snmp.get_value_type(v)
        ds.append("DS:{0}:{1}:{2}:U:U".format(k.lower(), type.upper(), heartbeat))
    return ds

def mk_rrd_filename(device, *args):
    ''' create a rrd filename based on the collected object '''
    parts = list()
    dev_name = device.sysName
    for arg in args:
        parts.append( arg.replace(".", "-") )
    return os.path.join(dev_name, "{0}.rrd".format("-".join(parts)))
