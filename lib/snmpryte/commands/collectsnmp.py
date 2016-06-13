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

import snmpryte
import snmpryte.snmp
from snmpryte.snmp.host.interface import HostInterface
from snmpryte.snmp.vendor.cisco.cbqos import CiscoCBQOS

from snmpryte.commands import BaseCommand
from snmpryte import constants as C
from snmpryte.utils import *

class CollectSnmpCommand(BaseCommand):

    def __init__(self, daemonize=False):
        super(CollectSnmpCommand, self).__init__(daemonize)
        self.parser.add_argument('--data', action='store_true',
                                 help='Show configuration CBQOS data for device(s)')
        self.parser.add_argument('devices', type=str, nargs='*',
                                 default=C.DEFAULT_DEVICES,
                                 help='list of devices to query')

    def run(self):
        args = self.parser.parse_args()
        if not args.datadir or not os.path.exists(args.datadir):
            logging.error("Path to data directory does not exist: %s", args.datadir)
            return 1
        setup_logging(args.verbose)
        logging.debug("beginning data collection")
        cfg = C.load_config()
        pool = Pool(processes=C.DEFAULT_WORKERS)
        logging.debug("created pool of workers")
        for device in args.devices:
            logging.info("handing off %s to worker", device)
            res = pool.apply_async(process_device, (device, args))
        pool.close()
        logging.debug("closed pool of workers")
        pool.join()


def process_device(device, args):
    try:
        msnmp = snmpryte.snmp.SNMPSession(host=device)
        cbqos = CiscoCBQOS(msnmp)
        process_policers(cbqos, args)
        process_interfaces(cbqos, args)
    except TypeError as e:
        logging.error("encountered error with %s; skipping to next device: %s", device, str(e))

def process_policers(cbqos, args):
    for key, data in cbqos.data.iteritems():
        if 'cbQosObjectsType' not in data:
            continue
        if data['cbQosObjectsType'] != 'police':
            continue
        # process the policer data
        conf = get_data(CiscoCBQOS.DATA, data)
        profile_stat = CiscoCBQOS.STAT.copy()
        profile_stat.update(HostInterface.STAT)
        for k in CiscoCBQOS.DATA.keys():
            if k in data and snmpryte.snmp.value_is_metric(data[k]):
                if 'Rate' in k:
                    profile_stat[k] = data[k]
        profile_strip = CiscoCBQOS.XLATE.copy()
        profile_strip.update(HostInterface.XLATE)
        values = get_data(profile_stat, data, profile_strip)
        process_data_instance(cbqos, args, CiscoCBQOS.NAME, key, conf, values)

def process_interfaces(cbqos, args):
    for key, data in cbqos.interfaces.iteritems():
        conf = get_data(HostInterface.DATA, data)
        values = get_data(HostInterface.STAT, data, HostInterface.XLATE)
        process_data_instance(cbqos, args, HostInterface.NAME, key, conf, values)

def process_data_instance(cbqos, args, name, key, conf, values):
    ''' '''
    if not values:
        return
    if args.data:
        if name == 'interface':
            pprint.pprint({key: cbqos.interfaces[key]})
        else:
            pprint.pprint({key: cbqos.policers[key]})
    json_path = mk_json_filename(cbqos, name, key)
    db = get_db_backend()
    if db.backend == 'rrd':
        db.path = json_path.replace('json', 'rrd')
    record_stats(db, values)
    record_data(json_path, conf, args)

def record_data(path, data, args):
    path = os.path.join(args.datadir, path)
    data2 = { k: snmpryte.snmp.mk_pretty_value(v) for (k, v) in data.iteritems() }
    if '_do_graph' not in data2:
        data2['_do_graph'] = True
    if os.path.exists(path):
        return
    snmpryte.utils.json2path(data2, path)

def record_stats(db, data):
    db.write(data)

def get_data(template, data, xlate={}):
    values = dict()
    for k in template:
        newk = clean_name(k, xlate)
        if k in data:
            values[newk] = data[k]
        else:
            values[newk] = 0
    return values

def clean_name(name, xlate):
    for k,v in xlate.iteritems():
        name = name.replace(k, v, 1)
    return name

