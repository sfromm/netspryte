# Written by Stephen Fromm <stephenf nero net>
# Copyright (C) 2016-2017 University of Oregon
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
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
from pysnmp.proto.rfc1902 import Counter32

class CiscoCBQOS(CiscoDevice):

    NAME = 'cbqos'

    ATTRS = {
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
        'ifHC' : '',
        'if'   : '',
    }

    def __init__(self, snmp):
        self.snmp = snmp
        self.data = dict()
        super(CiscoCBQOS, self).__init__(snmp)
        if CiscoDevice.BASE_OID not in str(self.sysObjectID):
            logging.debug("skipping cbqos check on non-cisco device %s", self.sysName)
            return None
        logging.info("inspecting %s for cbqos data", snmp.host)
        host = netspryte.snmp.host.interface.HostInterface(self.snmp)
        self.interfaces = host.interfaces
        self.data = self._get_configuration()
        logging.info("done inspecting %s for cbqos data", snmp.host)

    def _get_configuration(self):
        ''' get cbqos objects '''
        data = dict()
        attrs = netspryte.snmp.get_snmp_data(self.snmp, self, CiscoCBQOS.NAME,
                                             CiscoCBQOS.ATTRS, CiscoCBQOS.CONVERSION)
        metrics = netspryte.snmp.get_snmp_data(self.snmp, self, CiscoCBQOS.NAME,
                                               CiscoCBQOS.STAT, CiscoCBQOS.CONVERSION)
        interfaces = { k['index']: k for k in self.interfaces }
        skip_instances = [ k for k in attrs.keys() if '.' not in k ]

        # merge related instances into together for a coherent view
        for k, v in attrs.iteritems():
            if k in skip_instances:
                continue
            data[k] = self.initialize_instance(CiscoCBQOS.NAME, k)
            local_attrs = v.copy()
            if 'cbQosParentObjectsIndex' in v and v['cbQosParentObjectsIndex'] != 0:
                local_attrs['parent'] = k.split('.')[0] + "." + str(v['cbQosParentObjectsIndex'])

            # Pull in attributes from the cbqos config index.
            # The cbQosConfigIndex is used to identify the configuration,
            # which does not change regardless of number of times and where it is used.
            cfg_index = str(v['cbQosConfigIndex'])
            if cfg_index in skip_instances:
                local_attrs = safe_update(local_attrs, attrs[cfg_index])

            # Pull in attributes from the base/parent for this particular cbqos object type.
            # This is loosely related to the cbQosParentsObjectIndex, but just cuts to the
            # top of the hierarchy.
            base = k.split('.')[0]
            if base in attrs:
                local_attrs = safe_update(local_attrs, attrs[base])

            # If the cbQosIfIndex is present, pull in the related attributes for the
            # interface in question.
            if 'cbQosIfIndex' in local_attrs:
                ifidx = str(local_attrs['cbQosIfIndex'])
                local_attrs = safe_update(local_attrs, interfaces[ifidx]['attrs'])

            # The MIB erroneously marks this as a COUNTER64 to get the requisite number of bits
            # but it behaves like a GAUGE.  Unfortunately, there is no GAUGE64 object.  So ...
            # convert it to an int() so that it is treated like a GAUGE.
            if 'cbQosPoliceCfgRate64' in local_attrs:
                local_attrs['cbQosPoliceCfgRate64'] = int(local_attrs['cbQosPoliceCfgRate64'])
            data[k]['attrs'] = local_attrs
            data[k]['presentation'] = dict()
            if k in metrics:
                local_metrics = metrics[k].copy()
                local_metrics = safe_update(local_metrics, interfaces[ifidx]['metrics'])
                # Push the policer configured rate into the metrics dict
                if 'cbQosPoliceCfgRate64' in local_attrs:
                    local_metrics['cbQosPoliceCfgRate64'] = local_attrs['cbQosPoliceCfgRate64']

                # Finally, attach metrics to this measurement instance
                data[k]['metrics'] = local_metrics
                # In the event that not all STATs are returned
                # (eg not available or supported),
                # go back and put them in the recorded metrics for this measurement
                # instance.  Fake a COUNTER value of 0.
                for stat in CiscoCBQOS.STAT.keys():
                    if stat not in data[k]['metrics']:
                        data[k]['metrics'][stat] = Counter32(0)

        for key in data.keys():
            if key in skip_instances:
                continue
            data[key]['presentation']['title'] = self.get_policy_map_name(key, data)
            data[key]['presentation']['description'] = "{0}:{1}".format(data[key]['presentation']['title'], data[key].get('ifAlias', 'NA'))
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
            if 'cbQosObjectsType' in data['attrs'] and data['attrs']['cbQosObjectsType'] == 'police':
                policers.append(data)
        return policers

    def get_policy_map_name(self, idx, data_dict):
        key = 'cbQosPolicyMapName'
        if key not in data_dict[idx]['attrs']:
            return self.get_policy_map_name(data_dict[idx]['attrs']['parent'], data_dict)
        else:
            return data_dict[idx]['attrs'][key]

    def get_class_map_name(self, idx, data_dict):
        key = 'cbQosCMName'
        if key not in data[idx]['attrs']:
            return self.get_policy_map_name(data[idx]['attrs']['parent'], data_dict)
        else:
            return data_dict[idx]['attrs'][key]
