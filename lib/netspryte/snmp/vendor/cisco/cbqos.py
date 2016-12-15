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
import netspryte.snmp
import netspryte.snmp.host.interface
from netspryte.snmp.vendor.cisco import CiscoDevice
from netspryte.utils import *

class CiscoCBQOS(CiscoDevice):

    NAME = 'cbqos'

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

    XLATE = {
        'cbQos' : '',
        '64'    : '',
        'Bit'   : '',
    }

    def __init__(self, snmp):
        self.snmp = snmp
        super(CiscoCBQOS, self).__init__(snmp)
        if CiscoDevice.BASE_OID not in str(self.sysObjectID):
            logging.debug("skipping cbqos check on non-cisco device %s", self.sysName)
            return None
        logging.info("inspecting %s for cbqos data", snmp.host)
        host = netspryte.snmp.host.interface.HostInterface(self.snmp)
        self.interfaces = host.interfaces
        self.data = self._get_configuration()

    def _get_configuration(self):
        ''' get cbqos objects '''
        data = netspryte.snmp.get_snmp_data(self.snmp, self, CiscoCBQOS.NAME,
                                            CiscoCBQOS.DATA, CiscoCBQOS.CONVERSION)
        stat = netspryte.snmp.get_snmp_data(self.snmp, self, CiscoCBQOS.NAME,
                                            CiscoCBQOS.STAT, CiscoCBQOS.CONVERSION)
        interfaces = { k['_idx']: k for k in self.interfaces }
        skip_instances = [ k for k in data.keys() if '.' not in k ]

        # merge related instances into together for a coherent view
        for key in data.keys():
            if key in skip_instances:
                continue
            if 'cbQosParentObjectsIndex' in data[key] and data[key]['cbQosParentObjectsIndex'] != 0:
                data[key]['parent'] = key.split('.')[0] + "." + str(data[key]['cbQosParentObjectsIndex'])
            cfg_index = str(data[key]['cbQosConfigIndex'])
            if cfg_index in skip_instances:
                data[key] = safe_update(data[key], data[cfg_index])
            base = key.split('.')[0]
            if base in data:
                data[key] = safe_update(data[key], data[base])
            if 'cbQosIfIndex' in data[key]:
                ifidx = str(data[key]['cbQosIfIndex'])
                data[key] = safe_update(data[key], interfaces[ifidx])
            # The MIB erroneously marks this as a COUNTER64 to get the requisite number of bits
            # but it behaves like a GAUGE.  Unfortunately, there is no GAUGE64 object.  So ...
            # convert it to an int() so that it is treated like a GAUGE.
            if 'cbQosPoliceCfgRate64' in data[key]:
                data[key]['cbQosPoliceCfgRate64'] = int(data[key]['cbQosPoliceCfgRate64'])

        # merge stat and data
        merge_dicts(stat, data)

        # Set the meta information for the object
        # handled separately because it requires all of instance 'data' to be set.
        for key in data.keys():
            if key in skip_instances:
                continue
            data[key]['_title'] = self.get_policy_map_name(key, data)
            data[key]['_description'] = "{0}:{1}".format(data[key]['_title'], data[key].get('ifAlias', 'NA'))
        return data

    @property
    def policy_maps(self):
        ''' get policy maps '''
        return self.data

    @property
    def class_maps(self):
        ''' get class maps '''
        return self.data

    @property
    def policers(self):
        ''' get policer information '''
        policers = list()
        for data in self.data:
            if 'cbQosObjectsType' in data and data['cbQosObjectsType'] == 'police':
                policers.append(data)
        return policers

    def get_policy_map_name(self, idx, data_dict):
        key = 'cbQosPolicyMapName'
        if key not in data_dict[idx]:
            return self.get_policy_map_name(data_dict[idx]['parent'], data_dict)
        else:
            return data_dict[idx][key]

    def get_class_map_name(self, idx, data_dict):
        key = 'cbQosCMName'
        if key not in data[idx]:
            return self.get_policy_map_name(data[idx]['parent'], data_dict)
        else:
            return data_dict[idx][key]
