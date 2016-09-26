#!/usr/bin/python

#import cgitb
#cgitb.enable()

import cgi
import netspryte
from netspryte import constants as C
from netspryte.utils import *
from netspryte.db.rrd import *
import time

EXPIRES = 300 # number of seconds into the future to expire the image
form = cgi.FieldStorage()
start = form.getvalue('start', None)
end = form.getvalue('end', 'now')
graph_def = form.getvalue('gdef', None)
id = form.getvalue('id', None)
cfg = C.load_config()
dbs = get_db_backend()

if start is not None and start in C.get_config(cfg, 'rrd', 'start', None, [], islist=True):
    img = None
    data_sets = get_data_instances_by_id()
    if id in data_sets:
        for db in dbs:
            if db.backend == 'rrd':
                img = rrd_graph_data_instance(data_sets[id], cfg, graph_def, start, end)
        if img is not None:
            expires = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime(time.time() + EXPIRES))
            print "Content-Type: image/png\nContent-Length: %d\nExpires: %s\n" % (len(img), expires)
            print img
