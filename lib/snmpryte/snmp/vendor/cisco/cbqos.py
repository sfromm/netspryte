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
import pprint

class CiscoCBQOS():

    CONF = {
        'cbQosIfType'                 : '1.3.6.1.4.1.9.9.166.1.1.1.1.2',
        'cbQosPolicyDirection'        : '1.3.6.1.4.1.9.9.166.1.1.1.1.3',
        'cbQosIfIndex'                : '1.3.6.1.4.1.9.9.166.1.1.1.1.4',
        'cbQosConfigIndex'            : '1.3.6.1.4.1.9.9.166.1.5.1.1.2',
        'cbQosObjectsType'            : '1.3.6.1.4.1.9.9.166.1.5.1.1.3',
        'cbQosParentObjectsIndex'     : '1.3.6.1.4.1.9.9.166.1.5.1.1.4',
        'cbQosPolicyMapName'          : '1.3.6.1.4.1.9.9.166.1.6.1.1.1',
        'cbQosCMName'                 : '1.3.6.1.4.1.9.9.166.1.7.1.1.1',
        'cbQosPoliceCfgRate'          : '1.3.6.1.4.1.9.9.166.1.12.1.1.1',
        'cbQosPoliceCfgBurstSize'     : '1.3.6.1.4.1.9.9.166.1.12.1.1.2',
        'cbQosPoliceCfgExtBurstSize'  : '1.3.6.1.4.1.9.9.166.1.12.1.1.3',
        'cbQosPoliceCfgConformAction' : '1.3.6.1.4.1.9.9.166.1.12.1.1.4',
        'cbQosPoliceCfgExceedAction'  : '1.3.6.1.4.1.9.9.166.1.12.1.1.6',
        'cbQosPoliceCfgViolateAction' : '1.3.6.1.4.1.9.9.166.1.12.1.1.8',
        'cbQosPoliceCfgRate64'        : '1.3.6.1.4.1.9.9.166.1.12.1.1.11',
    }

    STAT = {
        'cbQosPoliceConformedPkt'     : '1.3.6.1.4.1.9.9.166.1.17.1.1.2',
        'cbQosPoliceConformedPkt64'   : '1.3.6.1.4.1.9.9.166.1.17.1.1.3',
        'cbQosPoliceConformedByte'    : '1.3.6.1.4.1.9.9.166.1.17.1.1.5',
        'cbQosPoliceConformedByte64'  : '1.3.6.1.4.1.9.9.166.1.17.1.1.6',
        'cbQosPoliceConformedBitRate' : '1.3.6.1.4.1.9.9.166.1.17.1.1.7',
        'cbQosPoliceExceededPkt'      : '1.3.6.1.4.1.9.9.166.1.17.1.1.9',
        'cbQosPoliceExceededPkt64'    : '1.3.6.1.4.1.9.9.166.1.17.1.1.10',
        'cbQosPoliceExceededByte'     : '1.3.6.1.4.1.9.9.166.1.17.1.1.12',
        'cbQosPoliceExceededByte64'   : '1.3.6.1.4.1.9.9.166.1.17.1.1.13',
        'cbQosPoliceExceededBitRate'  : '1.3.6.1.4.1.9.9.166.1.17.1.1.14',
        'cbQosPoliceViolatedPkt'      : '1.3.6.1.4.1.9.9.166.1.17.1.1.16',
        'cbQosPoliceViolatedPkt64'    : '1.3.6.1.4.1.9.9.166.1.17.1.1.17',
        'cbQosPoliceViolatedByte'     : '1.3.6.1.4.1.9.9.166.1.17.1.1.19',
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
        'cbQosPoliceConformAction': {
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
        'cbQosPoliceExceedAction': {
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
        'cbQosPoliceViolateAction': {
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

    def __init__(self, snmp):
        self.snmp = snmp
        host = snmpryte.snmp.host.interface.HostInterface(self.snmp)
        self.interfaces = host.interfaces
        self.objects = self._get_configuration()

    def _get_configuration(self):
        ''' get cbqos objects '''
        objects = snmpryte.snmp.get_snmp_data(self.snmp, CiscoCBQOS.CONF, CiscoCBQOS.CONVERSION)

        instances = [ k for k in objects.keys() if '.' not in k ]
        # merge related instances into together for a coherent view
        for obj in objects.keys():
            if obj in instances:
                continue
            if 'cbQosParentObjectsIndex' in objects[obj]:
                objects[obj]['parent'] = obj.split('.')[0] + "." + str(objects[obj]['cbQosParentObjectsIndex'])
            cfg_index = str(objects[obj]['cbQosConfigIndex'])
            if cfg_index in instances:
                objects[obj].update(objects[cfg_index])
            base = obj.split('.')[0]
            if base in objects:
                objects[obj].update(objects[base])
            if 'cbQosIfIndex' in objects[obj]:
                ifidx = str(objects[obj]['cbQosIfIndex'])
                objects[obj].update( self.interfaces[ifidx] )

        return objects


    def get_policy_maps(self):
        ''' get policy maps '''
        return self.objects

    def get_class_maps(self):
        ''' get class maps '''
        return self.objects

    def get_policers(self):
        ''' get policer information '''
        for k in self.objects.keys():
            if 'cbQosObjectsType' in objects[k]:
                print objects[k]['cbQosObjectsType']

    def get_policer_stats(self):
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
                if index in self.objects:
                    stats[index].update(self.objects[index])
                    parent = self.objects[index]['parent']
                    if parent not in stats:
                        stats[parent] = self.objects[parent]
            stats[index][oid['name']] = obj[1]
        return stats
