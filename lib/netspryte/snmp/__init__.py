# Written by Stephen Fromm <stephenf nero net>
# Copyright (C) 2015-2017 University of Oregon
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

import time
import logging
from pysnmp.entity.rfc3413.oneliner import cmdgen
from pysnmp.proto.rfc1902 import (
    Counter32,
    Counter64,
    Gauge32,
    Integer,
    Integer32,
    IpAddress,
    OctetString,
    ObjectIdentifier,
    TimeTicks,
    Unsigned32,
)
from pysnmp.proto.rfc1905 import (
    EndOfMibView,
)

import netspryte.utils
from netspryte import constants as C
from netspryte.errors import NetspryteSNMPError
from netspryte.utils.timer import Timer


def value_is_metric(arg):
    if isinstance(arg, Counter32) or isinstance(arg, Counter64):
        return True
    elif isinstance(arg, Gauge32):
        return True
    elif isinstance(arg, int):
        return True
    else:
        return False


def get_value_type(arg):
    if isinstance(arg, Counter32) or isinstance(arg, Counter64):
        return 'counter'
    elif isinstance(arg, TimeTicks):
        return 'counter'
    elif isinstance(arg, Gauge32) or isinstance(arg, Integer) or isinstance(arg, Integer32):
        return 'gauge'
    elif isinstance(arg, Unsigned32):
        return 'gauge'
    else:
        return 'gauge'


def mk_pretty_value(arg):
    ''' Inspect SNMP value type and return it '''
    if isinstance(arg, ObjectIdentifier):
        return arg.prettyPrint()
    if isinstance(arg, Integer):
        return arg.prettyPrint()
    if isinstance(arg, Gauge32):
        return arg.prettyPrint()
    if isinstance(arg, Counter32) or isinstance(arg, Counter64):
        return arg.prettyPrint()
    if isinstance(arg, IpAddress):
        return str(arg.prettyPrint())
    if isinstance(arg, OctetString):
        return clean_octet_string(arg)
    if isinstance(arg, EndOfMibView):
        return arg.prettyPrint()
    return arg


def value_is_integer(arg):
    if isinstance(arg, Counter32) or \
       isinstance(arg, Counter64) or \
       isinstance(arg, Gauge32) or \
       isinstance(arg, Integer) or \
       isinstance(arg, Integer32) or \
       isinstance(arg, int):
        return True
    elif isinstance(arg, str) and arg.isdigit():
        return True
    else:
        return False


def clean_octet_string(arg):
    try:
        return arg.asOctets().decode(arg.encoding).strip()
    except UnicodeDecodeError:
        return arg.asOctets()


def strip_oid(oid, arg):
    ''' strip a substring OID from another OID '''
    if oid[-1] != ".":
        oid = oid + "."
    if oid not in arg:
        return arg
    result = arg.replace(oid, '')
    if result[0] == '.':
        return result.lstrip('.')
    else:
        return result


def deconstruct_oid(arg, oid_set):
    ''' break an OID into parts '''
    oid = dict()
    oid['oid'] = arg
    for k in list(oid_set.keys()):
        index = strip_oid(oid_set[k], arg)
        if index != arg:
            oid['base'] = oid_set[k]
            oid['name'] = k
            oid['index'] = index
            break
    return oid


def get_snmp_data(snmp, host, cls_name, snmp_oids, snmp_conversion, chunk=None):
    '''
    Take a dictionary of snmp oids and return object with data.
    Arguments:
    - snmp: SNMPSession object
    - host: SNMP query module object
    - cls_name: Name of SNMP query module
    - snmp_oids: dict of variable name to OID to query
    - snmp_conversion: dict of key/value pairs of substitutions for snmp responses
    - chunk: optional argument for splitting queries up into smaller chunks.  This is the chunk size.
    Returns a dictionary indexed by the SNMP index for the table.
    '''
    t = Timer("snmp query {0}-{1}".format(snmp.host, cls_name))
    t.start_timer()
    data = dict()
    results = list()
    if chunk:
        oids = list(snmp_oids.values())
        qry_oids = [oids[i:i + chunk] for i in range(0, len(oids), chunk)]
        for qry_set in qry_oids:
            results.extend(snmp.walk(*qry_set))
    else:
        results = snmp.walk(*[oid for oid in list(snmp_oids.values())])
    for obj in results:
        logging.debug("Processing %s OID=%s, value=%s", snmp.host, obj[0], obj[1])
        oid = deconstruct_oid(obj[0], snmp_oids)
        if 'index' not in oid:
            logging.debug("No match for OID=%s", obj[0])
            continue
        index = oid['index']

        if index not in data:
            data[index] = dict()
        if oid['name'] in snmp_conversion and value_is_integer(obj[1]) and \
           int(obj[1]) in snmp_conversion[oid['name']]:
            data[index][oid['name']] = snmp_conversion[oid['name']][int(obj[1])]
        else:
            data[index][oid['name']] = obj[1]
    t.stop_timer()
    return data


class SNMPSession(object):
    ''' a class to handle SNMP queries '''

    def __init__(self, **kwargs):
        ''' Initialize a MSnmp object '''
        self._host      = C.DEFAULT_SNMP_HOST
        self._port      = C.DEFAULT_SNMP_PORT
        self._timeout   = C.DEFAULT_SNMP_TIMEOUT
        self._retries   = C.DEFAULT_SNMP_RETRIES
        self._version   = C.DEFAULT_SNMP_VERSION
        self._community = C.DEFAULT_SNMP_COMMUNITY
        self._username  = C.DEFAULT_SNMP_USERNAME
        self._level     = C.DEFAULT_SNMP_LEVEL
        self._privacy   = C.DEFAULT_SNMP_PRIVACY
        self._authkey   = C.DEFAULT_SNMP_AUTHKEY
        self._privkey   = C.DEFAULT_SNMP_PRIVKEY
        self._bulk      = C.DEFAULT_SNMP_BULK
        self._cache     = dict()   # (oids) -> [ time, result ]

        for key in list(kwargs.keys()):
            if hasattr(self, key):
                setattr(self, key, kwargs[key])

        if self._version == '3':
            pass
        else:
            self._auth = cmdgen.CommunityData(self._community)
        self._cmdgen = cmdgen.CommandGenerator()
        self._transport = cmdgen.UdpTransportTarget((self._host, self._port),
                                                    timeout=self._timeout, retries=self._retries)

    @property
    def host(self):
        return self._host

    @host.setter
    def host(self, arg):
        self._host = arg

    @property
    def port(self):
        return self._port

    @port.setter
    def port(self, arg):
        try:
            self._port = int(arg)
        except ValueError:
            raise ValueError("SNMP port must be an integer")

    @property
    def timeout(self):
        return self._timeout

    @timeout.setter
    def timeout(self, arg):
        try:
            self._timeout = int(arg)
        except ValueError:
            raise ValueError("SNMP timeout must be an integer")

    @property
    def retries(self):
        return self._retries

    @retries.setter
    def retries(self, arg):
        try:
            self._retries = int(arg)
        except ValueError:
            raise ValueError("SNMP retries must be an integer")

    @property
    def version(self):
        return self._version

    @version.setter
    def version(self, arg):
        if arg in C.DEFAULT_ALLOWED_SNMP_VERSIONS:
            self._version = arg
        else:
            raise ValueError("SNMP version must be one of: " + ", ".join(C.DEFAULT_ALLOWED_SNMP_VERSIONS))

    @property
    def community(self):
        return self._community

    @community.setter
    def community(self, arg):
        if isinstance(arg, str):
            self._community = arg
        else:
            raise ValueError("SNMP community must be a string")

    @property
    def bulk(self):
        return self._bulk

    @bulk.setter
    def bulk(self, arg):
        try:
            if arg is False:
                self._bulk = False
            else:
                self._bulk = int(arg)
                if self._bulk <= 0:
                    self._bulk = False
        except ValueError:
            raise ValueError("Bulk value must be an integer")

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, arg):
        self._username = arg

    @property
    def level(self):
        return self._level

    @level.setter
    def level(self, arg):
        if arg in C.DEFAULT_ALLOWED_SNMP_LEVELS:
            self._level = arg
        else:
            raise ValueError("SNMPv3 level must be one of: " + ", ".join(C.DEFAULT_ALLOWED_SNMP_LEVELS))

    def expire_cache(self):
        ''' expire the cache '''
        self._cache = dict()

    def _snmp_varbind_to_list(self, varbind):
        ''' take a oid object and return a tuple of ( numerical_oid, value ) '''
        oid = varbind[0]
        value = varbind[1]
        value_type = value.__class__.__name__
        if not value_is_metric(value):
            value = mk_pretty_value(value)
        num_oid = oid.prettyPrint()
        if hasattr(oid, 'getOid'):
            num_oid = str(oid.getOid())
        if isinstance(value, EndOfMibView):
            logging.debug("reached end of mib view with %s", num_oid)
        logging.debug("snmp varbind %s: %s=%s (%s)", self.host, num_oid, mk_pretty_value(value), value_type)
        return (num_oid, value)

    def _cache_results(self, oids, result):
        ''' tie results to oid query set in cache '''
        self._cache[oids] = [time.time(), result]

    def _cmd(self, cmd, *oids):
        ''' apply a generic snmp operation '''
        results = []
        errorIndication, errorStatus, errorIndex, varBindTable = cmd(
            self._auth,
            self._transport,
            *oids
        )
        if errorIndication:
            raise NetspryteSNMPError(str(errorIndication))
        if errorStatus:
            raise NetspryteSNMPError(errorStatus.prettyPrint())
        if cmd in [self._cmdgen.getCmd, self._cmdgen.setCmd]:
            results = [self._snmp_varbind_to_list(varbind) for varbind in varBindTable]
        else:
            results = [self._snmp_varbind_to_list(varbind)
                       for row in varBindTable for varbind in row if not isinstance(varbind[1], EndOfMibView)]
        return results

    def _cache_or_cmd(self, cmd, *oids):
        ''' pull result from cache or query host for OIDS '''
        if oids in self._cache:
            t, result = self._cache[oids]
            if (time.time() - t) < C.DEFAULT_SNMP_CACHE_TIMEOUT:
                return result
        result = self._cmd(cmd, *oids)
        self._cache_results(oids, result)
        return result

    def get(self, *oids):
        ''' perform snmp get queries for list of snmp oids '''
        results = self._cache_or_cmd(self._cmdgen.getCmd, *oids)
        return results

    def walk(self, *oids):
        ''' perform snmp getnext or getbulk queries for list of snmp oids '''
        results = list()
        if self.version == '1' or not self.bulk:
            return self._cache_or_cmd(self._cmdgen.nextCmd, *oids)
        args = [0, self.bulk] + list(oids)
        try:
            return self._cache_or_cmd(self._cmdgen.bulkCmd, *args)
        except NetspryteSNMPError as e:
            logging.error("caught snmp error with %s: %s", self.host, str(e))
            return results

    def set(self, *args):
        ''' set an oid value via SET '''
        pass
        if len(args) % 2 != 0:
            raise ValueError("require an even number of arguments for SET")
