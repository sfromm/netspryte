# Written by Stephen Fromm <stephenf nero net>
# Copyright (C) 2017 University of Oregon
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

from flask import (Flask, jsonify, render_template, request, make_response, url_for)
from playhouse.flask_utils import object_list
import collections
import functools
import operator
import time
import urllib.parse

from netspryte.utils import get_db_backend
from netspryte import constants as C
from netspryte.manager import MeasurementInstance, MeasurementClass, Manager, Tag, Host
from netspryte.db.rrd import *

LIMIT = 10


class ReverseProxied(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        script_name = environ.get('HTTP_X_SCRIPT_NAME', '')
        if script_name:
            environ['SCRIPT_NAME'] = script_name
            path_info = environ['PATH_INFO']
            if path_info.startswith(script_name):
                environ['PATH_INFO'] = path_info[len(script_name):]

        scheme = environ.get('HTTP_X_SCHEME', '')
        if scheme:
            environ['wsgi.url_scheme'] = scheme
        return self.app(environ, start_response)


app = Flask(__name__)
app.jinja_env.add_extension('jinja2.ext.loopcontrols')
app.wsgi_app = ReverseProxied(app.wsgi_app)


def get_graph_definitions(mclasses, extended_data=False):
    cfg = C.load_config()
    graph_defs = list()
    for cls in mclasses:
        def_ids = C.get_config(cfg, "rrd_{0}".format(cls), 'graph',
                               None, None, islist=True)
        if def_ids:
            if not extended_data:
                graph_id = def_ids[0]
                graph_title = C.get_config(cfg, graph_id, 'title', None, None)
                graph_defs.append((graph_id, graph_title))
            else:
                for graph_id in def_ids:
                    graph_title = C.get_config(cfg, graph_id, 'title', None, None)
                    graph_defs.append((graph_id, graph_title))
    return graph_defs


def get_graph_periods(all_periods=False):
    cfg = C.load_config()
    graph_periods = list()
    start_periods = C.DEFAULT_RRD_START
    if all_periods:
        graph_periods = list(start_periods)
    else:
        graph_periods.append(start_periods[0])
    return graph_periods


@app.route('/', methods=['GET'])
def hello():
    mgr = Manager()
    measurement_classes = list()
    measurement_instances = list()
    tag = request.args.get('tag', None)
    cls = request.args.get('class', None)
    host = request.args.get('host', None)
    instance = request.args.get('instance', None)
    all_tags = mgr.get_all(Tag).order_by(Tag.name)
    extended_data = False
    related = dict()
    for m in mgr.get_all(MeasurementClass):
        measurement_classes.append(m.name)
    if not cls and not host and not instance and not tag:
        cls = 'interface'
    measurement_instances = mgr.get_instances_by_tags([tag], True)
    if cls:
        measurement_instances = mgr.get_instances_by_class(cls, True)
    elif host:
        measurement_instances = mgr.get_instances_by_host(host, True)
    elif instance:
        measurement_instances = mgr.get_instances("name", instance, True)
        extended_data = True
    graph_defs = get_graph_definitions(measurement_classes, extended_data)
    graph_periods = get_graph_periods(extended_data)
    clauses = filter_measurement_instance_clauses()
    measurement_instances = (measurement_instances
                             .where(functools.reduce(operator.and_, clauses))
                             .order_by(MeasurementInstance.description))

    # Create a list of related items.
    for i in measurement_instances:
        i_class = "class=%s" % i.measurement_class.name
        i_host = "host=%s" % i.host.name
        if i_class not in related:
            related[i_class] = i.measurement_class.description
        if i_host not in related:
            related[i_host] = i.host.name
    if measurement_instances.count() == 1:
        this_minst = measurement_instances[0]
        for r in this_minst.relationships:
            key = "instance=%s" % r.to_measurement_instance.name
            related[key] = r.to_measurement_instance.title

    return object_list('netspryte.html',
                       measurement_instances,
                       context_variable="measurement_instances",
                       paginate_by=LIMIT,
                       graph_defs=graph_defs,
                       graph_periods=graph_periods,
                       related=collections.OrderedDict(sorted(related.items())),
                       tags=all_tags,
                       measurement_classes=measurement_classes)


@app.route('/netspryte/graph', methods=['GET'])
def get_graph():
    ''' for supplied id, create graph '''
    EXPIRES = 120
    mgr = Manager()
    start = request.args.get('start', None)
    end = request.args.get('end', 'now')
    graph_def = request.args.get('gdef', None)
    name = request.args.get('name', None)
    cfg = C.load_config()
    dbs = get_db_backend()
    mi = mgr.get(MeasurementInstance, name=name)
    if not mi:
        return
    response = make_response()
    if start is not None:
        img = None
        for db in dbs:
            if db.backend == 'rrd':
                img = rrd_graph_data_instance(mgr.to_dict(mi), cfg, graph_def, start, end)
        if img is not None:
            expires = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime(time.time() + EXPIRES))
            response = make_response(img)
            response.headers['Content-Type'] = 'image/png'
            response.headers['Content-Length'] = len(img)
            response.headers['Expires'] = expires
    return response


@app.route('/api/v1.0/host/<host>', methods=['GET'])
def get_host(host):
    mgr = Manager()
    modinst = mgr.get(Host, name=host)
    if not modinst:
        modinst = dict()
    return jsonify(mgr.to_dict(modinst))


@app.route('/api/v1.0/hosts', methods=['GET'])
def get_hosts():
    ''' return list of available hosts '''
    mgr = Manager()
    result = {'hosts': list()}
    for h in mgr.get_all(Host):
        result['hosts'].append(mgr.to_dict(h))
    return jsonify(result)


@app.route('/api/v1.0/host_instances/<host>', methods=['GET'])
def get_host_instances(host):
    mgr = Manager()
    modinst = mgr.get(Host, name=host)
    if not modinst:
        return jsonify({})
    result = {'instances': [q.name for q in modinst.measurement_instances]}
    return jsonify(result)


@app.route('/api/v1.0/class/<arg>', methods=['GET'])
def get_measurement_class(arg):
    mgr = Manager()
    modinst = mgr.get(MeasurementClass, name=arg)
    if not modinst:
        modinst = dict()
    return jsonify(mgr.to_dict(modinst))


@app.route('/api/v1.0/classes', methods=['GET'])
def get_measurement_classes():
    ''' return list of available measurement classes '''
    mgr = Manager()
    result = {'classes': list()}
    for m in mgr.get_all(MeasurementClass):
        result['classes'].append(mgr.to_dict(m))
    return jsonify(result)


@app.route('/api/v1.0/instance/<arg>', methods=['GET'])
def get_measurement_instance(arg):
    mgr = Manager()
    modinst = mgr.get(MeasurementInstance, name=arg)
    if not modinst:
        modinst = dict()
    return jsonify(mgr.to_dict(modinst))


@app.route('/api/v1.0/instances', methods=['GET'])
def get_measurement_instances():
    ''' return list of available measurement instances '''
    mgr = Manager()
    result = {'instances': list()}
    for m in mgr.get_all(MeasurementInstance):
        result['instances'].append(m.name)
    result['instances'].sort()
    return jsonify(result)


@app.route('/api/v1.0/tags', methods=['GET'])
def get_tags():
    ''' return list of tags '''
    mgr = Manager()
    result = {'tags': list()}
    for m in mgr.get_all(Tag):
        result['tags'].append(m.name)
    result['tags'].sort()
    return jsonify(result)


@app.teardown_appcontext
def close_db(error):
    pass


def filter_measurement_instance_clauses():
    clauses = [
        (MeasurementInstance.has_metrics == True),
        (MeasurementInstance.title.is_null(False)),
        (MeasurementInstance.description.is_null(False)),
        (MeasurementInstance.title != ""),
        (MeasurementInstance.description != ""),
    ]
    return clauses


@app.template_filter('clean_querystring')
def clean_querystring(request_args, *keys_to_remove, **new_values):
    # We'll use this template filter in the pagination include. This filter
    # will take the current URL and allow us to preserve the arguments in the
    # querystring while replacing any that we need to overwrite. For instance
    # if your URL is /?q=search+query&page=2 and we want to preserve the search
    # term but make a link to page 3, this filter will allow us to do that.
    querystring = dict((key, value) for key, value in request_args.items())
    for key in keys_to_remove:
        querystring.pop(key, None)
    querystring.update(new_values)
    return urllib.parse.urlencode(querystring)


def get_related_interface(measurement_instance, ifindex):
    mgr = Manager()
    intf = mgr.get(MeasurementInstance, host=measurement_instance.host.id, index=ifindex)
    return intf


def get_related_interface_attributes(measurement_instance, ifindex):
    intf = get_related_interface(measurement_instance, ifindex)
    attrs = intf.interface_attrs.get()
    return attrs


@app.template_filter('get_related_interface_name')
def get_related_interface_name(measurement_instance, ifindex):
    intf = get_related_interface(measurement_instance, ifindex)
    return intf.name


@app.template_filter('get_related_interface_ifalias')
def get_related_interface_ifalias(measurement_instance, ifindex):
    intf = get_related_interface(measurement_instance, ifindex)
    attrs = intf.interface_attrs.get()
    return attrs['ifAlias']


@app.template_filter('get_related_interface_ifdescr')
def get_related_interface_ifalias(measurement_instance, ifindex):
    intf = get_related_interface(measurement_instance, ifindex)
    attrs = intf.interface_attrs.get()
    return attrs['ifDescr']


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
