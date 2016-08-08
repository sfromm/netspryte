# Written by Stephen Fromm <stephenf nero net>
# (C) 2015-2016 University of Oregon
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
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

import argparse
import os
import sys
import logging
import glob
import pprint
from multiprocessing import Process, Pool

import netspryte

from netspryte.commands import BaseCommand
from netspryte import constants as C
from netspryte.utils import *
from netspryte.db.rrd import *

from jinja2 import Environment, FileSystemLoader
import jinja2.exceptions

class MkGraphsCommand(BaseCommand):

    def __init__(self, daemonize=False):
        super(MkGraphsCommand, self).__init__(daemonize)
        self.parser.add_argument('globs', type=str, nargs='*',
                                 help='list of directory globs to graph')

    def run(self):
        args = self.parser.parse_args()
        if not args.datadir or not os.path.exists(args.datadir):
            logging.error("Path to data directory does not exist: %s", args.datadir)
            return 1
        if not C.DEFAULT_WWWDIR or not os.path.exists(C.DEFAULT_WWWDIR):
            logging.error("Path to data directory does not exist: %s", C.DEFAULT_WWWDIR)
            return 1
        setup_logging(args.verbose)
        logging.debug("beginning graph creation")
        cfg = C.load_config()
        data_globs = list()
        data_set = list()
        if args.globs:
            for dev in args.globs:
                data_globs.extend(
                    glob.glob("{0}/{1}/*.json".format(args.datadir, dev))
                )
        else:
            data_globs.extend(
                glob.glob("{0}/*/*.json".format(args.datadir))
            )
        pool = Pool(processes=C.DEFAULT_WORKERS)
        logging.debug("created pool of workers")
        for json_path in sorted(data_globs):
            (data, graph_defs) = self.graph_data_instance(args, json_path, cfg)
            if data is None:
               continue
            data_set.append(data)
            if args.nofork:
                do_graph_instance(graph_defs)
            else:
                res = pool.apply_async(do_graph_instance, (graph_defs,))
        pool.close()
        logging.debug("closed pool of workers")
        pool.join()
        self.template_html(C.DEFAULT_WWWDIR, cfg, data_set)

    def graph_data_instance(self, args, json_path, cfg):
        data = parse_json_from_file(json_path)
        if data is None:
            logging.warn("failed to read from json: %s", json_path)
            return (None, None)
        rrd_path = json_path.replace('json', 'rrd')
        if self.skip_data_instance(data):
            logging.debug("skipping graph generation of %s", rrd_path)
            return data
        data['_graphs'] = list()
        base_rrd_opts = list()
        graph_defs = list()
        section = "rrd_{0}".format(data['_class'])
        graphs = C.get_config(cfg, section, 'graph', None, None, islist=True)
        for graph in graphs:
            graph_defs.extend(self.graph_data_definitions(data, graph, rrd_path, cfg))
            for graph_def in graph_defs:
                data['_graphs'].append(get_relative_png_path(graph_def[0]))
        return (data, graph_defs)

    def skip_data_instance(self, data):
        if '_do_graph' not in data:
            return True
        elif not data['_do_graph']:
            return True
        elif '_class' not in data:
            return True
        else:
            return False

    def get_graph_cmd_opts(self, cfg):
        base_rrd_opts = list()
        for name, val in cfg.items('rrd'):
            if name in ['start', 'step', 'heartbeat']:
                continue
            base_rrd_opts.append('--{0}'.format(name))
            if val:
                base_rrd_opts.append(val)
        return base_rrd_opts

    def graph_data_definitions(self, data_set, graph, rrd_path, cfg):
        graph_opts = list()
        rrd_opts = self.get_graph_cmd_opts(cfg)
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
        return self.graph_period_definitions(rrd_path, rrd_opts, graph_opts, graph, cfg)

    def graph_period_definitions(self, rrd_path, rrd_opts, graph_opts, graph, cfg):
        graph_defs = list()
        start_periods = C.get_config(cfg, 'rrd', 'start', None, None, islist=True)
        for period in start_periods:
            graph_defs.append( (
                get_absolute_png_path(rrd_path, graph, period),
                rrd_opts + ['--start', period],
                graph_opts
            ) )
        return graph_defs

    def template_html(self, wwwdir, cfg, data_set):
        graph_periods = list()
        data_class = dict()
        start_periods = C.get_config(cfg, 'rrd', 'start', None, None, islist=True)
        graph_periods.append(start_periods[0])
        detail_graph_periods = [ x for x in start_periods if x not in graph_periods ]
        env = Environment(
            loader=FileSystemLoader(wwwdir)
        )
        for k in data_set:
            if k['_class'] not in data_class:
                data_class[k['_class']] = list()
            data_class[k['_class']].append(k)

        for cls in data_class.keys():
            self.do_template_html(
                env,
                C.get_config(cfg, 'general', 'html_template', None, None),
                os.path.join(wwwdir, "{0}.html".format(cls)),
                sorted(data_class[cls], key=lambda k: k['_title']),
                graph_periods
            )
        for data in data_set:
            title = clean_string(data['_id'])
            self.do_template_html(
                env,
                C.get_config(cfg, 'general', 'html_template', None, None),
                os.path.join(wwwdir, "{0}.html".format(title)),
                [data],
                detail_graph_periods
            )

    def do_template_html(self, env, template, path, data_set, graph_periods):
        try:
            logging.info("creating html template %s", path)
            template = env.get_template(template)
            data2path(template.render(data_sets=data_set, graph_periods=graph_periods), path)
            os.chmod(path, 0664)
        except jinja2.exceptions.TemplateNotFound as e:
            logging.error("failed to find template: %s", str(e))

def get_absolute_png_path(rrd_path, graph, period):
    basedir = os.path.basename( os.path.dirname(rrd_path) )
    basename = os.path.basename(rrd_path)
    basename_list = basename.rsplit('.', 1)
    basename_list[0] += "-{0}".format(graph)
    basename_list[0] += period
    basename_list[-1] = 'png'
    return os.path.join(C.DEFAULT_WWWDIR, basedir, ".".join(basename_list))

def get_relative_png_path(arg):
    head, tail = os.path.split(arg)
    subdir = os.path.basename(head)
    return os.path.join(subdir, tail)

def do_graph_instance(graph_defs):
    dbs = get_db_backend()
    for db in dbs:
        for graph_def in graph_defs:
            if db.backend == 'rrd':
                rrd_graph(graph_def[0], graph_def[1], graph_def[2])
