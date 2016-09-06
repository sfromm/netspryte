# Written by Stephen Fromm <stephenf nero net>
# (C) 2015-2016 University of Oregon
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

import datetime
import os
import pwd
import ConfigParser
from netspryte.errors import *

def get_config(p, section, key, env_var, default, boolean=False, integer=False, islist=False):
    if env_var is not None:
        value = os.environ.get(env_var, None)
        if value is not None:
            return value
    if p is not None:
        try:
            value = p.get(section, key)
        except:
            return default
        if integer:
            return int(value)
        elif boolean:
            if value is None:
                return False
            value = str(value)
            if value.lower() in ['true', 't', 'y', '1', 'yes']:
                return True
            else:
                return False
        elif islist:
            return [ x.lstrip() for x in value.split('\n') ]
        else:
            return value
    print value
    return default

def load_config():
    ''' load config file '''
    p = ConfigParser.ConfigParser()
    path0 = os.getenv("NETSPRYTE_CONFIG", None)
    if path0 is not None:
        path0 = os.path.expanduser(path0)
    path1 = os.getcwd() + "/netspryte.cfg"
    path2 = "/etc/netspryte/netspryte.cfg"

    for path in [path0, path1, path2]:
        if path is not None and os.path.exists(path):
            try:
                p.read(path)
            except ConfigParser.Error as e:
                raise NetspryteError("Configuration error: " + str(e))
            return p
    return None

p = load_config()

DEFAULTS = 'general'
DEFAULT_SNMP_HOST      = get_config(p, DEFAULTS, "snmp_host",      "NETSPRYTE_SNMP_HOST",      "localhost")
DEFAULT_SNMP_PORT      = get_config(p, DEFAULTS, "snmp_port",      "NETSPRYTE_SNMP_PORT",      161)
DEFAULT_SNMP_TIMEOUT   = get_config(p, DEFAULTS, "snmp_timeout",   "NETSPRYTE_SNMP_TIMEOUT",   5)
DEFAULT_SNMP_RETRIES   = get_config(p, DEFAULTS, "snmp_retries",   "NETSPRYTE_SNMP_RETRIES",   2)
DEFAULT_SNMP_VERSION   = get_config(p, DEFAULTS, "snmp_version",   "NETSPRYTE_SNMP_VERSION",   "2c")
DEFAULT_SNMP_COMMUNITY = get_config(p, DEFAULTS, "snmp_community", "NETSPRYTE_SNMP_COMMUNITY", "public")
DEFAULT_SNMP_USERNAME  = get_config(p, DEFAULTS, "snmp_username",  "NETSPRYTE_SNMP_USERNAME",  "na")
DEFAULT_SNMP_LEVEL     = get_config(p, DEFAULTS, "snmp_level",     "NETSPRYTE_SNMP_LEVEL",     "na")
DEFAULT_SNMP_PRIVACY   = get_config(p, DEFAULTS, "snmp_PRIVACY",   "NETSPRYTE_SNMP_PRIVACY",   "na")
DEFAULT_SNMP_AUTHKEY   = get_config(p, DEFAULTS, "snmp_authkey",   "NETSPRYTE_SNMP_AUTHKEY",   "na")
DEFAULT_SNMP_PRIVKEY   = get_config(p, DEFAULTS, "snmp_privkey",   "NETSPRYTE_SNMP_PRIVKEY",   "na")
DEFAULT_SNMP_BULK      = get_config(p, DEFAULTS, "snmp_bulk",      "NETSPRYTE_SNMP_BULK",      20)

DEFAULT_VERBOSE        = get_config(p, DEFAULTS, "verbose",        "NETSPRYTE_VERBOSE",        0)
DEFAULT_LOG_LEVEL      = get_config(p, DEFAULTS, "loglevel",       "NETSPRYTE_LOG_LEVEL",      0)
DEFAULT_LOG_FORMAT     = get_config(p, DEFAULTS, "logformat",      "NETSPRYTE_LOG_FORMAT",     '%(asctime)s: [%(process)s:%(levelname)s] %(message)s')
DEFAULT_LOG_NAME       = get_config(p, DEFAULTS, "logname",        "NETSPRYTE_LOG_NAME",       "netspryte")

DEFAULT_DATABASE       = get_config(p, DEFAULTS, "database",       "NETSPRYTE_DATABASE",       ["rrd"], islist=True)
DEFAULT_WORKERS        = get_config(p, DEFAULTS, "workers",        "NETSPRYTE_WORKERS",        4, integer=True)
DEFAULT_DEVICES        = get_config(p, DEFAULTS, "devices",        "NETSPRYTE_DEVICES",        ["localhost"], islist=True)
DEFAULT_DATADIR        = get_config(p, DEFAULTS, "datadir",        "NETSPRYTE_DATADIR",        "data")
DEFAULT_WWWDIR         = get_config(p, DEFAULTS, "wwwdir",         "NETSPRYTE_WWWDIR",         "www")
DEFAULT_CHECKSUM       = get_config(p, DEFAULTS, "checksum",       "NETSPRYTE_CHECKSUM",       "sha1")

DEFAULT_ALLOWED_SNMP_VERSIONS = ['1', '2c', '3']
DEFAULT_ALLOWED_SNMP_LEVELS   = ['authNoPriv', 'authPriv']

DEFAULT_RRD_STEP       = get_config(p, 'rrd', 'step',      "NETSPRYTE_RRD_STEP",      60, integer=True)
DEFAULT_RRD_HEARTBEAT  = get_config(p, 'rrd', 'heartbeat', "NETSPRYTE_RRD_HEARTBEAT", 5,  integer=True)
DEFAULT_RRD_START      = get_config(p, 'rrd', 'start',     "NETSPRYTE_RRD_START",     ["-1d", "-1w", "-1m", "-1y"], islist=True)
DEFAULT_RRD_RRA =        get_config(p, 'rrd', 'rra',       "NETSPRYTE_RRD_RRA",       [ "RRA:AVERAGE:0.5:1:10080",
                                                                                        "RRA:AVERAGE:0.5:120:2232",
                                                                                        "RRA:AVERAGE:0.5:1440:1098",
                                                                                        "RRA:MAX:0.5:1:10080",
                                                                                        "RRA:MAX:0.5:120:2232",
                                                                                        "RRA:MAX:0.5:1440:1098" ], islist=True)

DEFAULT_INFLUXDB_HOST     = get_config(p, 'influxdb', 'host',     'NETSPRYTE_INFLUXDB_HOST',     'localhost')
DEFAULT_INFLUXDB_PORT     = get_config(p, 'influxdb', 'port',     'NETSPRYTE_INFLUXDB_PORT',     8086, integer=True)
DEFAULT_INFLUXDB_USER     = get_config(p, 'influxdb', 'user',     'NETSPRYTE_INFLUXDB_USER',     'root')
DEFAULT_INFLUXDB_PASSWORD = get_config(p, 'influxdb', 'password', 'NETSPRYTE_INFLUXDB_PASSWORD', 'root')
DEFAULT_INFLUXDB_DATABASE = get_config(p, 'influxdb', 'database', 'NETSPRYTE_INFLUXDB_DATABASE', 'netspryte')
