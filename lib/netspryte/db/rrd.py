# Written by Stephen Fromm <stephenf nero net>
# Copyright (C) 2016- 2017 University of Oregon
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
import netspryte.utils
from netspryte.db import BaseDatabaseBackend
from netspryte import constants as C


class RrdDatabaseBackend(BaseDatabaseBackend):

    def __init__(self, backend, **kwargs):
        super(RrdDatabaseBackend, self).__init__(backend, **kwargs)
        if 'path' in kwargs:
            self.path = kwargs['path']
        else:
            self.path = None
        self.measurement_instance = None

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, arg):
        self._path = arg

    def write(self, data, xlate=None):
        ''' write data to rrd database '''
        if self.measurement_instance is None:
            logging.error("unable to write to rrd without a measurement_instance property")
            return None
        host = self.measurement_instance.host.name
        mcls = self.measurement_instance.measurement_class.name
        transport = self.measurement_instance.measurement_class.transport
        inst = self.measurement_instance.index
        if not self.path:
            self.path = mk_rrd_filename(host, mcls, inst)
        if not os.path.exists(self.path):
            mcls_types = self.measurement_instance.measurement_class.metric_type
            mcls_types = netspryte.utils.xlate_metric_names(mcls_types, xlate)
            rrd_create(self.path, C.DEFAULT_RRD_STEP, mcls_types, C.DEFAULT_RRD_RRA)
        return rrd_update(self.path, data)


def rrd_create(path, step, data_types, rra):
    ''' create a rrd '''
    args = [path, '--step', str(step)]
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    try:
        data_sources = mk_rrd_ds(data_types)
        logging.debug("RRD STEP: %s", step)
        logging.debug("RRD DS: %s", " ".join(data_sources))
        logging.debug("RRD RRA: %s", " ".join(rra))
        logging.info("creating rrd %s", path)
        rrdtool.create(str(path), '--step', str(step), data_sources, *rra)
    except (rrdtool.OperationalError, rrdtool.ProgrammingError) as e:
        logging.error("failed to create rrd %s: %s", path, str(e))


def rrd_update(path, data, ts=time.time()):
    ''' update rrd '''
    template = list()
    values = list()
    for k, v in list(data.items()):
        template.append(k.lower())
        if hasattr(v, 'prettyPrint'):
            values.append(v.prettyPrint())
        else:
            values.append(str(v))
        flat_template = ":".join(template)
    flat_values = ":".join(values)
    try:
        logging.info("updating rrd %s", path)
        logging.debug("updating rrd %s with template: %s %s:%s", path, flat_template, ts, flat_values)
        rrdtool.update(str(path), '--template', flat_template, "%s:%s" % (ts, flat_values))
    except (rrdtool.OperationalError, rrdtool.ProgrammingError) as e:
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
    except (rrdtool.OperationalError, rrdtool.ProgrammingError) as e:
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
    except (rrdtool.OperationalError, rrdtool.ProgrammingError) as e:
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
        logging.warn("tuning maximum value to %s for all DS in rrd %s", ds_max, path)
        tune_ds = list()
        for tune in rrd_get_ds_list(path):
            tune_ds.append("--maximum")
            tune_ds.append(str("%s:%s" % (tune, ds_max)))
        rrdtool.tune(path, tune_ds)
    except (rrdtool.OperationalError, rrdtool.ProgrammingError) as e:
        logging.error("failed to tune max for %s: %s", path, str(e))


def mk_rrd_ds(data):
    ''' take in dictionary of collected values and return a list of DS '''
    ds = list()
    heartbeat = C.DEFAULT_RRD_STEP * C.DEFAULT_RRD_HEARTBEAT
    for k, v in list(data.items()):
        ds.append("DS:{0}:{1}:{2}:U:U".format(k.lower(), v.upper(), heartbeat))
    return ds


def mk_rrd_filename(device, *args):
    ''' create a rrd filename based on the collected object '''
    return "{0}.rrd".format(netspryte.utils.mk_measurement_instance_filename(device, *args))


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
    if data is None:
        return image
    rrd_path = netspryte.utils.mk_measurement_instance_filename(data['host']['name'],
                                                                data['measurement_class']['name'],
                                                                data['index'])
    start = str(start)
    rrd_path += ".rrd"
    section = "rrd_{0}".format(data['measurement_class']['name'])
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
        if name in ['start', 'step', 'heartbeat', 'end']:
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
                graph_opts.append(str(opt))
        else:
            rrd_opts.append('--{0}'.format(name))
            if val:
                rrd_opts.append(val)
    if '--title' not in rrd_opts:
        rrd_opts.append('--title')
        rrd_opts.append(str(data_set['title']))
    return (rrd_opts, graph_opts)
