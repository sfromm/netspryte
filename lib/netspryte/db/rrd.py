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
import re

import netspryte.snmp
from netspryte.db import *
from netspryte.utils import *
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
    ''' create a graph for rrd
    if path is "-", image is returned as part of dictionary.
    Keys in dictionary:
    graph_end
    graph_height
    graph_left
    graph_start
    graph_top
    graph_width
    image
    image_height
    image_width
    value_max
    value_min
    '''
    data = dict()
    if path != "-" and not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    try:
        logging.info("creating graph %s", path)
        data = rrdtool.graphv(path, rrd_opts, graph_opts)
    except rrdtool.error as e:
        logging.error("failed to create graph %s: %s", path, str(e))
    return data

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

def rrd_get_ds_list(path):
    ''' return list of DS in rrd '''
    ds_list = list()
    for arg in rrd_info(path):
        if 'max' in arg:
            m = re.match(r'^ds\[(\w+)\]\.', arg)
            if m:
                ds_list.append(m.group(1))
    return ds_list

def rrd_tune_ds_max(path, ds_max):
    ''' tune max for all DS in rrd '''
    try:
        logging.debug("tuning maximum value for all DS in rrd %s", path)
        tune_ds = list()
        for tune in rrd_get_ds_list(path):
            tune_ds.append("--maximum")
            tune_ds.append(str("%s:%s" % (tune, ds_max)))
        rrdtool.tune(path, tune_ds)
    except rrdtool.error as e:
        logging.error("failed to tune max for %s: %s", path, str(e))

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

def rrd_preserve(rrd_path):
    ''' rename existing RRD for preservation
    performs a rename operation on the RRD
    '''
    mtime = int(os.path.getmtime(rrd_path))
    dirname = os.path.dirname(rrd_path)
    basename = os.path.basename(rrd_path)
    os.rename(rrd_path,
              os.path.join(dirname,
                           "backup-{0}-{1}".format(str(mtime), basename)
              )
    )

def rrd_graph_data_instance(data, cfg, graph_def, start, end='now'):
    '''
    a more friendly way of generating a graph from rrdtool
    Arguments:
    data - data from json file of data instance
    cfg - netspryte configuration via C.load_config()
    graph_def - thing to graph, defined in configuration
    start - start time for graph
    Returns a variable with image as string.
    '''
    image = None
    json_path = data['_path']
    if data is None:
        return image
    rrd_path = json_path.replace('json', 'rrd')
    if skip_data_instance(data):
        return image
    section = "rrd_{0}".format(data['_class'])
    graphs = C.get_config(cfg, section, 'graph', None, None, islist=True)
    if graph_def in graphs:
        (rrd_opts, graph_opts) = _rrd_graph_data_definitions(data, graph_def, rrd_path, cfg)
        g = rrd_graph("-", rrd_opts + ['--start', start, '--end', end], graph_opts)
        if 'image' in g:
            image = g['image']
    return image

def _rrd_graph_command_opts(cfg):
    base_rrd_opts = list()
    for name, val in cfg.items('rrd'):
        if name in ['start', 'step', 'heartbeat']:
            continue
        if name == 'watermark' and val == C.DEFAULT_RRD_WATERMARK:
            val = time.strftime(C.DEFAULT_STRFTIME, time.localtime(time.time()))
        base_rrd_opts.append('--{0}'.format(name))
        if val:
            base_rrd_opts.append(val)
    return base_rrd_opts

def _rrd_graph_data_definitions(data_set, graph, rrd_path, cfg):
    graph_opts = list()
    rrd_opts = _rrd_graph_command_opts(cfg)
    for name, val in cfg.items(graph):
        if name in ['def', 'cdef', 'vdef', 'graph']:
            for opt in C.get_config(cfg, graph, name, None, None, islist=True):
                if '%s' in opt and name == 'def':
                    opt = opt % rrd_path
                graph_opts.append( opt )
        else:
            rrd_opts.append('--{0}'.format(name))
            if val:
                rrd_opts.append(val)
    if '--title' not in rrd_opts:
        rrd_opts.append('--title')
        rrd_opts.append( str(data_set['_title']) )
    return (rrd_opts, graph_opts)
