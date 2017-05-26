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

from flask import (Flask, jsonify, render_template, request, make_response)
from playhouse.flask_utils import object_list
import collections
import time
import urllib

from netspryte.utils import *
from netspryte import constants as C
from netspryte.manager import *
from netspryte.db.rrd import *

LIMIT = 10

app = Flask(__name__)
app.jinja_env.add_extension('jinja2.ext.loopcontrols')

def get_graph_defs(mclasses, extended_data=False):
    cfg = C.load_config()
    graph_defs = list()
    for cls in mclasses:
        gd = C.get_config(cfg, "rrd_{0}".format(cls), 'graph',
                          None, None, islist=True)
        if gd:
            if extended_data:
                graph_defs.extend(gd)
            else:
                graph_defs.append(gd[0])
    return graph_defs

def get_graph_periods(all_periods=False):
    cfg = C.load_config()
    graph_periods = list()
    start_periods = C.get_config(cfg, 'rrd', 'start', None, None, islist=True)
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
    all_tags = mgr.get_all(Tag)
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
    graph_defs = get_graph_defs(measurement_classes, extended_data)
    graph_periods = get_graph_periods(extended_data)
    measurement_instances = measurement_instances.where(~(MeasurementInstance.metrics >> None))

    # Create a list of related items.
    for i in measurement_instances:
        i_class = "class=%s" % i.measurement_class.name
        i_host = "host=%s" % i.host.name
        if i_class not in related:
            related[i_class] = i.measurement_class.description
        if i_host not in related:
            related[i_host] = i.host.name
    if measurement_instances.count() == 1:
        for i in measurement_instances:
            if i.measurement_class.name == 'cbqos':
                key = "instance=%s.interface.%s" % (i.name.split('.')[0], i.attrs['ifIndex'])
                related[key] = "Interface %s" % i.attrs['ifDescr']

    return object_list('netspryte.html',
                       measurement_instances,
                       context_variable="measurement_instances",
                       paginate_by=LIMIT,
                       graph_defs=graph_defs,
                       graph_periods=graph_periods,
                       related=collections.OrderedDict(sorted(related.items())),
                       tags=all_tags,
                       measurement_classes=measurement_classes )

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
    if start is not None and start in C.get_config(cfg, 'rrd', 'start', None, [], islist=True):
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
    return jsonify( mgr.to_dict(modinst) )

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
        return jsonify( {} )
    result = { 'instances': [ q.name for q in modinst.measurement_instances ] }
    return jsonify( result )

@app.route('/api/v1.0/class/<arg>', methods=['GET'])
def get_measurement_class(arg):
    mgr = Manager()
    modinst = mgr.get(MeasurementClass, name=arg)
    if not modinst:
        modinst = dict()
    return jsonify( mgr.to_dict(modinst) )

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
    return jsonify( mgr.to_dict(modinst) )

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

@app.template_filter('can_graph')
def filter_graph_candidates(candidate):
    r = True
    if candidate.presentation is None:
        r = False
    elif candidate.presentation['title'] is None:
        r = False
    elif candidate.presentation['description'] is None or candidate.presentation['description'] == "":
        r = False
    elif candidate.measurement_class.name in ["entity", "ipnetwork"]:
        r = False
    elif 'ifType' in candidate.attrs and candidate.attrs['ifType'] in ["32", "49", "63", "77", "81", "134", "166"]:
        # Ignore the following ifTypes:
        # 32 - framerelay
        # 49 - aal5
        # 63 - isdn
        # 77 - lapd
        # 81 - ds0
        # 134 - atmSubInterface
        # 166 - mpls
        r = False
    elif 'ifAdminStatus' in candidate.attrs and candidate.attrs['ifAdminStatus'] == 'down':
        r = False
    elif 'cbQosObjectsType' in candidate.attrs and candidate.attrs['cbQosObjectsType'] != "police":
        r = False
    elif 'cbQosPolicyDirection' in candidate.attrs and candidate.attrs['cbQosPolicyDirection'] == 'input':
        r = False
    return r

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
    return urllib.urlencode(querystring)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
