# Written by Stephen Fromm <stephenf nero net>
# (C) 2015 University of Oregon
#
# This file is part of snmpryte
#
# snmpryte is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# snmpryte is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with snmpryte.  If not, see <http://www.gnu.org/licenses/>.

import datetime
import os
import pwd
import ConfigParser
from snmpryte.errors import *

def get_config(p, section, key, env_var, default):
    if env_var is not None:
        value = os.environ.get(env_var, None)
        if value is not None:
            return value
    if p is not None:
        try:
            return p.get(section, key)
        except:
            return default
    return default

def load_config():
    ''' load config file '''
    p = ConfigParser.ConfigParser()
    path0 = os.getenv("SNMPRYTE_CONFIG", None)
    if path0 is not None:
        path0 = os.path.expanduser(path0)
    path1 = os.getcwd() + "/snmpryte.cfg"

    for path in [path0, path1]:
        if path is not None and os.path.exists(path):
            try:
                p.read(path)
            except ConfigParser.Error as e:
                raise SnmpryteError("Configuration error: " + str(e))
            return p
    return None

p = load_config()

DEFAULTS = 'default'
DEFAULT_SNMP_HOST      = get_config(p, DEFAULTS, "snmp_host",      "SNMPRYTE_SNMP_HOST",      "localhost")
DEFAULT_SNMP_PORT      = get_config(p, DEFAULTS, "snmp_port",      "SNMPRYTE_SNMP_PORT",      161)
DEFAULT_SNMP_VERSION   = get_config(p, DEFAULTS, "snmp_version",   "SNMPRYTE_SNMP_VERSION",   "2c")
DEFAULT_SNMP_COMMUNITY = get_config(p, DEFAULTS, "snmp_community", "SNMPRYTE_SNMP_COMMUNITY", "public")
DEFAULT_SNMP_USERNAME  = get_config(p, DEFAULTS, "snmp_username",  "SNMPRYTE_SNMP_USERNAME",  "na")
DEFAULT_SNMP_LEVEL     = get_config(p, DEFAULTS, "snmp_level",     "SNMPRYTE_SNMP_LEVEL",     "na")
DEFAULT_SNMP_PRIVACY   = get_config(p, DEFAULTS, "snmp_PRIVACY",   "SNMPRYTE_SNMP_PRIVACY",   "na")
DEFAULT_SNMP_AUTHKEY   = get_config(p, DEFAULTS, "snmp_authkey",   "SNMPRYTE_SNMP_AUTHKEY",   "na")
DEFAULT_SNMP_PRIVKEY   = get_config(p, DEFAULTS, "snmp_privkey",   "SNMPRYTE_SNMP_PRIVKEY",   "na")
DEFAULT_SNMP_BULK      = get_config(p, DEFAULTS, "snmp_bulk",      "SNMPRYTE_SNMP_BULK",      20)

DEFAULT_VERBOSE        = get_config(p, DEFAULTS, "verbose",        "SNMPRYTE_VERBOSE",        False)
DEFAULT_LOG_LEVEL      = get_config(p, DEFAULTS, "loglevel",       "SNMPRYTE_LOG_LEVEL",      0)
DEFAULT_LOG_FORMAT     = get_config(p, DEFAULTS, "logformat",      "SNMPRYTE_LOG_FORMAT",     '%(asctime)s: [%(levelname)s] %(message)s')

DEFAULT_ALLOWED_SNMP_VERSIONS = ['1', '2c', '3']
DEFAULT_ALLOWED_SNMP_LEVELS   = ['authNoPriv', 'authPriv']
