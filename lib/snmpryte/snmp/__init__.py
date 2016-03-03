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
    TimeTicks,
    Unsigned32,
)
from snmpryte import constants as C

def mk_pretty_value(arg):
    ''' Inspect SNMP value type and return it '''
    if isinstance(arg, Counter32):
        return int(arg.prettyPrint())
    if isinstance(arg, OctetString):
        try:
            return arg.asOctets().decode(arg.encoding)
        except UnicodeDecodeError:
            return arg.asOctets()
    return arg

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
    for k in oid_set.keys():
        index = strip_oid(oid_set[k], arg)
        if index != arg:
            oid['base'] = oid_set[k]
            oid['name'] = k
            oid['index'] = index
            break
    return oid

def get_snmp_data(snmp, snmp_oids, snmp_conversion):
    ''' take a dictionary of snmp oids and return object with data '''
    objects = dict()
    results = snmp.walk( *[ oid for oid in snmp_oids.values() ] )
    for obj in results:
        logging.debug("Processing OID=%s, value=%s", obj[0], obj[1])
        oid = deconstruct_oid(obj[0], snmp_oids)
        if 'index' not in oid:
            continue
        index = oid['index']

        if index not in objects:
            objects[index] = {}
        if oid['name'] in snmp_conversion:
            objects[index][oid['name']] = snmp_oids[oid['name']][int(obj[1])]
        else:
            objects[index][oid['name']] = obj[1] 
    return objects

class SNMPSession(object):
    ''' a class to handle SNMP queries '''

    def __init__(self, **kwargs):
        ''' Initialize a MSnmp object '''
        self._host      = C.DEFAULT_SNMP_HOST
        self._port      = C.DEFAULT_SNMP_PORT
        self._version   = C.DEFAULT_SNMP_VERSION
        self._community = C.DEFAULT_SNMP_COMMUNITY
        self._username  = C.DEFAULT_SNMP_USERNAME
        self._level     = C.DEFAULT_SNMP_LEVEL
        self._privacy   = C.DEFAULT_SNMP_PRIVACY
        self._authkey   = C.DEFAULT_SNMP_AUTHKEY
        self._privkey   = C.DEFAULT_SNMP_PRIVKEY
        self._bulk      = C.DEFAULT_SNMP_BULK

        for key in kwargs.keys():
            if hasattr(self, key):
                setattr(self, key, kwargs[key])

        if self._version == '3':
            pass
        else:
            self._auth = cmdgen.CommunityData(self._community)
        self._cmdgen = cmdgen.CommandGenerator()
        self._transport = cmdgen.UdpTransportTarget((self._host, self._port))

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
        if isinstance(arg, basestring):
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

    @username.setter
    def level(self, arg):
        if arg in C.DEFAULT_ALLOWED_SNMP_LEVELS:
            self._level = arg
        else:
            raise ValueError("SNMPv3 level must be one of: " + ", ".join(C.DEFAULT_ALLOWED_SNMP_LEVELS))

    def _cmd(self, cmd, *oids):
        ''' apply a generic snmp operation '''
        results = []
        errorIndication, errorStatus, errorIndex, varBinds = cmd(
            self._auth,
            self._transport,
            *oids
        )
        if errorIndication:
            raise SnmpryteSNMPException(str(errorIndication))
        if errorStatus:
            raise SnmpryteSNMPException(errorStatus.prettyPrint())
        if cmd in [self._cmdgen.getCmd, self._cmdgen.setCmd]:
            for oid, value in varBinds:
                results.append(mk_pretty_value(value))
        else:
            for row in varBinds:
                for oid, value in row:
                    results.append((oid.prettyPrint(), mk_pretty_value(value)))
                    logging.debug("%s: %s=%s", self.host, oid.prettyPrint(), mk_pretty_value(value))
        return results

    def get(self, *oids):
        ''' perform snmp get queries for list of snmp oids '''
        results = self._cmd(self._cmdgen.getCmd, *oids)
        if len(results) == 1:
            results = results[0]
        return results

    def walk(self, *oids):
        ''' perform snmp getnext or getbulk queries for list of snmp oids '''
        results = []
        cmd_gen = cmdgen.CommandGenerator()
        if self.version == '1' or not self.bulk:
            return self._cmd(self._cmdgen.nextCmd, *oids)
        args = [0, self.bulk] + list(oids)
        return self._cmd(self._cmdgen.bulkCmd, *args)

    def set(self, *args):
        ''' set an oid value via SET '''
        pass
        if len(args) % 2 != 0:
            raise ValueError("require an even number of arguments for SET")
