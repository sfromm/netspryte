#!/usr/bin/python

import cgi

import netspryte
from netspryte import constants as C
from netspryte.utils import *
from netspryte.db.rrd import *

form = cgi.FieldStorage()
start = form.getvalue('start', None).lower()
graph_def = form.getvalue('gdef', None).lower()
id = form.getvalue('id', None).lower()
cfg = C.load_config()
dbs = get_db_backend()

if start in C.get_config(cfg, 'rrd', 'start', None, None, islist=True):
    img = None
    data_sets = get_instances_by_id()
    if id in data_sets:
        for db in dbs:
            if db.backend == 'rrd':
                img = rrd_graph_data_instance(data, cfg, start, graph_def)
        if img is not None:
            print "Content-Type: image/png\nContent-Length: %d\n" % len(img)
            print img
