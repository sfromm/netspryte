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

class MkHtmlCommand(BaseCommand):

    def __init__(self, daemonize=False):
        super(MkHtmlCommand, self).__init__(daemonize)
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
        logging.debug("beginning html creation")
        cfg = C.load_config()
        data_globs = list()
        data_set = get_data_instances_from_disjoined()
        json2path(data_set, os.path.join(C.DEFAULT_DATADIR, C.DEFAULT_DATA_JOINED))
        self.template_html(C.DEFAULT_WWWDIR, cfg, data_set)

    def template_html(self, wwwdir, cfg, data_set):
        graph_periods = list()
        data_class = dict()
        data_device = dict()

        start_periods = C.get_config(cfg, 'rrd', 'start', None, None, islist=True)
        graph_periods.append(start_periods[0])
        detail_graph_periods = [ x for x in start_periods ]

        env = Environment(
            loader=FileSystemLoader(wwwdir)
        )
        env.add_extension('jinja2.ext.loopcontrols')
        for k in data_set:
            if k['_class'] not in data_class:
                data_class[k['_class']] = list()
            data_class[k['_class']].append(k)
            logging.debug("adding %s to data class %s", k['_id'], k['_class'])
            device = k['_id'].split('.', 1)[0]
            device = device.replace('_', '.')
            if device not in data_device:
                data_device[device] = list()
            data_device[device].append(k)
            logging.debug("adding %s to device %s", k['_id'], device)

        # for each class of data
        for cls in data_class.keys():
            graph_defs = C.get_config(cfg, "rrd_{0}".format(cls), 'graph', None, None, islist=True)
            self.do_template_html(
                env,
                C.get_config(cfg, 'general', 'html_template', None, None),
                os.path.join(wwwdir, "{0}.html".format(cls)),
                sorted(data_class[cls], key=lambda k: k['_title']),
                graph_periods,
                [ graph_defs[0] ],
            )
        # for each device
        graph_defs = list()
        for cls in data_class.keys():
            graph_defs.extend(C.get_config(cfg, "rrd_{0}".format(cls), 'graph', None, None, islist=True))
        for device in data_device.keys():
            title = device
            self.do_template_html(
                env,
                C.get_config(cfg, 'general', 'html_template', None, None),
                os.path.join(wwwdir, "{0}.html".format(title)),
                self.sort_device_data_instances(data_device[device], '_idx'),
                graph_periods,
                graph_defs,
            )
        # for each data instance
        for data in data_set:
            title = clean_string(data['_id'])
            graph_defs = C.get_config(cfg, "rrd_{0}".format(data['_class']), 'graph', None, None, islist=True)
            self.do_template_html(
                env,
                C.get_config(cfg, 'general', 'html_template', None, None),
                os.path.join(wwwdir, "{0}.html".format(title)),
                [data],
                detail_graph_periods,
                graph_defs,
            )

    def do_template_html(self, env, template, path, data_set, graph_periods, graph_defs):
        try:
            logging.info("creating html template %s", path)
            template = env.get_template(template)
            data2path(template.render(data_sets=data_set,
                                      graph_periods=graph_periods,
                                      graph_defs=graph_defs,
                                      www_cgi_url=C.DEFAULT_WWW_CGI_URL),
                      path)
            os.chmod(path, 0664)
        except jinja2.exceptions.TemplateNotFound as e:
            logging.error("failed to find template: %s", str(e))

    def sort_device_data_instances(self, devlist, key='_idx'):
        data_class = dict()
        instances = list()
        for inst in devlist:
            if inst['_class'] not in data_class:
                data_class[inst['_class']] = list()
            data_class[inst['_class']].append(inst)
        for dclass in sorted(data_class.keys()):
            instances.extend( sorted(data_class[dclass], key=lambda k: float(k[key]) ) )
        return instances
