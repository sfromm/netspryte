# Written by Stephen Fromm <stephenf nero net>
# (C) 2016 University of Oregon
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

import logging
import snmpryte.snmp
import snmpryte.snmp.host.interface
from snmpryte.snmp.vendor.cisco import CiscoDevice
from snmpryte.utils import *

class CiscoCBQOS(CiscoDevice):

    DATA = {
        'cbQosIfType'                 : '1.3.6.1.4.1.9.9.166.1.1.1.1.2',
        'cbQosPolicyDirection'        : '1.3.6.1.4.1.9.9.166.1.1.1.1.3',
        'cbQosIfIndex'                : '1.3.6.1.4.1.9.9.166.1.1.1.1.4',
        'cbQosConfigIndex'            : '1.3.6.1.4.1.9.9.166.1.5.1.1.2',
        'cbQosObjectsType'            : '1.3.6.1.4.1.9.9.166.1.5.1.1.3',
        'cbQosParentObjectsIndex'     : '1.3.6.1.4.1.9.9.166.1.5.1.1.4',
        'cbQosPolicyMapName'          : '1.3.6.1.4.1.9.9.166.1.6.1.1.1',
        'cbQosCMName'                 : '1.3.6.1.4.1.9.9.166.1.7.1.1.1',
        'cbQosPoliceCfgBurstSize'     : '1.3.6.1.4.1.9.9.166.1.12.1.1.2',
        'cbQosPoliceCfgExtBurstSize'  : '1.3.6.1.4.1.9.9.166.1.12.1.1.3',
        'cbQosPoliceCfgConformAction' : '1.3.6.1.4.1.9.9.166.1.12.1.1.4',
        'cbQosPoliceCfgExceedAction'  : '1.3.6.1.4.1.9.9.166.1.12.1.1.6',
        'cbQosPoliceCfgViolateAction' : '1.3.6.1.4.1.9.9.166.1.12.1.1.8',
        'cbQosPoliceCfgRate64'        : '1.3.6.1.4.1.9.9.166.1.12.1.1.11',
    }

    STAT = {
        'cbQosPoliceConformedPkt64'   : '1.3.6.1.4.1.9.9.166.1.17.1.1.3',
        'cbQosPoliceConformedByte64'  : '1.3.6.1.4.1.9.9.166.1.17.1.1.6',
        'cbQosPoliceConformedBitRate' : '1.3.6.1.4.1.9.9.166.1.17.1.1.7',
        'cbQosPoliceExceededPkt64'    : '1.3.6.1.4.1.9.9.166.1.17.1.1.10',
        'cbQosPoliceExceededByte64'   : '1.3.6.1.4.1.9.9.166.1.17.1.1.13',
        'cbQosPoliceExceededBitRate'  : '1.3.6.1.4.1.9.9.166.1.17.1.1.14',
        'cbQosPoliceViolatedPkt64'    : '1.3.6.1.4.1.9.9.166.1.17.1.1.17',
        'cbQosPoliceViolatedByte64'   : '1.3.6.1.4.1.9.9.166.1.17.1.1.20',
        'cbQosPoliceViolatedBitRate'  : '1.3.6.1.4.1.9.9.166.1.17.1.1.21',
    }

    CONVERSION = {
        'cbQosPolicyDirection': {
            1 : 'input',
            2 : 'output'
        },
        'cbQosObjectsType': {
            1 : 'policymap',
            2 : 'classmap',
            3 : 'matchStatement',
            4 : 'queueing',
            5 : 'randomDetect',
            6 : 'trafficShaping',
            7 : 'police',
            8 : 'set',
            9 : 'compression'
        },
        'cbQosPoliceCfgConformAction': {
            1 : 'transmit',
            2 : 'setIpDSCP',
            3 : 'setIpPrecedence',
            4 : 'setQosGroup',
            5 : 'drop',
            6 : 'setMplsExp',
            7 : 'setAtmClp',
            8 : 'setFrDe',
            9 : 'setL2Cos',
            10 : 'setDiscardClass',
            11 : 'setMplsExpTopMost',
            12 : 'setIpDscpTunnel',
            13 : 'setIpPrecedenceTunnel',
        },
        'cbQosPoliceCfgExceedAction': {
            1 : 'transmit',
            2 : 'setIpDSCP',
            3 : 'setIpPrecedence',
            4 : 'setQosGroup',
            5 : 'drop',
            6 : 'setMplsExp',
            7 : 'setAtmClp',
            8 : 'setFrDe',
            9 : 'setL2Cos',
            10 : 'setDiscardClass',
            11 : 'setMplsExpTopMost',
            12 : 'setIpDscpTunnel',
            13 : 'setIpPrecedenceTunnel',
        },
        'cbQosPoliceCfgViolateAction': {
            1 : 'transmit',
            2 : 'setIpDSCP',
            3 : 'setIpPrecedence',
            4 : 'setQosGroup',
            5 : 'drop',
            6 : 'setMplsExp',
            7 : 'setAtmClp',
            8 : 'setFrDe',
            9 : 'setL2Cos',
            10 : 'setDiscardClass',
            11 : 'setMplsExpTopMost',
            12 : 'setIpDscpTunnel',
            13 : 'setIpPrecedenceTunnel',
        },
    }

    NAME = 'cbqos'

    XLATE = {
        'cbQos' : '',
        '64'    : '',
        'Bit'   : '',
    }

    def __init__(self, snmp):
        self.snmp = snmp
        super(CiscoCBQOS, self).__init__(snmp)
        logging.info("inspecting %s for cbqos data", snmp.host)
        host = snmpryte.snmp.host.interface.HostInterface(self.snmp)
        self.interfaces = host.interfaces
        data = self._get_configuration()
        self._data = data
        stat = self.get_cbqos_stats()
        merge_dicts(data, stat)
        self._data = data

    def _get_configuration(self):
        ''' get cbqos objects '''
        data = snmpryte.snmp.get_snmp_data(self.snmp, CiscoCBQOS.DATA, CiscoCBQOS.CONVERSION)
        instances = [ k for k in data.keys() if '.' not in k ]
        # merge related instances into together for a coherent view
        for key in data.keys():
            if key in instances:
                continue
            if 'cbQosParentObjectsIndex' in data[key]:
                data[key]['parent'] = key.split('.')[0] + "." + str(data[key]['cbQosParentObjectsIndex'])
            cfg_index = str(data[key]['cbQosConfigIndex'])
            if cfg_index in instances:
                data[key].update(data[cfg_index])
            base = key.split('.')[0]
            if base in data:
                data[key].update(data[base])
            if 'cbQosIfIndex' in data[key]:
                ifidx = str(data[key]['cbQosIfIndex'])
                data[key].update( self.interfaces[ifidx] )
            # The MIB erroneously marks this as a COUNTER64 to get the requisite number of bits
            # but it behaves like a GAUGE.  Unfortunately, there is no GAUGE64 object.  So ...
            # convert it to an int() so that it is treated like a GAUGE.
            if 'cbQosPoliceCfgRate64' in data[key]:
                data[key]['cbQosPoliceCfgRate64'] = int(data[key]['cbQosPoliceCfgRate64'])
            # Set the meta information for the object
            data[key]['_class'] = CiscoCBQOS.NAME
            data[key]['_idx'] = key
            data[key]['_title'] = self.get_policy_map_name(key)
            data[key]['_description'] = "{0}:{1}".format(data[key]['_title'], data[key].get('ifAlias', 'NA'))
        return data

    @property
    def data(self):
        return self._data

    @property
    def policy_maps(self):
        ''' get policy maps '''
        return self._data

    @property
    def class_maps(self):
        ''' get class maps '''
        return self._data

    @property
    def policers(self):
        ''' get policer information '''
        return self._data

    def get_cbqos_stats(self):
        ''' get policer stats '''
        stats = dict()
        results = self.snmp.walk( *[ k for k in CiscoCBQOS.STAT.values() ] )
        for obj in results:
            logging.debug("Processing OID=%s, value=%s", obj[0], obj[1])
            oid = snmpryte.snmp.deconstruct_oid(obj[0], CiscoCBQOS.STAT)
            if 'index' not in oid:
                continue
            index = oid['index']

            if index not in stats:
                stats[index] = {}
                if index in self.data:
                    stats[index].update(self.data[index])
                    parent = self.data[index]['parent']
                    if parent not in stats:
                        stats[parent] = self.data[parent]
            stats[index][oid['name']] = obj[1]
        return stats

    def get_policy_map_name(self, idx):
        key = 'cbQosPolicyMapName'
        if key not in self.data[idx]:
            return self.get_policy_map_name(self.data[idx]['parent'])
        else:
            return self.data[idx][key]

    def get_class_map_name(self, key):
        key = 'cbQosCMName'
        if key not in self.data[idx]:
            return self.get_policy_map_name(self.data[idx]['parent'])
        else:
            return self.data[idx][key]
