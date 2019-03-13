# Written by Stephen Fromm <stephenf nero net>
# Copyright (C) 2019 University of Oregon
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
import ipaddress
from netspryte.snmp.vendor.cisco import CiscoDevice
from netspryte.utils import safe_update
from netspryte.utils.timer import Timer
from pysnmp.proto.rfc1902 import Counter32

class CiscoRttMon(CiscoDevice):

    NAME = 'rttmon'
    DESCRIPTION = "Cisco RTT Monitoring"
    ATTR_MODEL = 'CiscoRttMonAttrs'
    METRIC_MODEL = 'CiscoRttMonMetrics'

    ATTRS = {
        'rttMonCtrlAdminOwner': '1.3.6.1.4.1.9.9.42.1.2.1.1.2',
        'rttMonCtrlAdminTag': '1.3.6.1.4.1.9.9.42.1.2.1.1.3',
        'rttMonCtrlAdminRttType': '1.3.6.1.4.1.9.9.42.1.2.1.1.4',
        'rttMonCtrlAdminThreshold': '1.3.6.1.4.1.9.9.42.1.2.1.1.5',
        'rttMonCtrlAdminFrequency': '1.3.6.1.4.1.9.9.42.1.2.1.1.6',
        'rttMonCtrlAdminTimeout': '1.3.6.1.4.1.9.9.42.1.2.1.1.7',
        'rttMonCtrlAdminStatus': '1.3.6.1.4.1.9.9.42.1.2.1.1.9',
        'rttMonLatestRttOperSense': '1.3.6.1.4.1.9.9.42.1.2.10.1.2',
        'crttMonIPEchoAdminTargetAddrType': '1.3.6.1.4.1.9.9.572.1.1.1.1',
        'crttMonIPEchoAdminTargetAddress': '1.3.6.1.4.1.9.9.572.1.1.1.2',
        'crttMonIPEchoAdminSourceAddrType': '1.3.6.1.4.1.9.9.572.1.1.1.3',
        'crttMonIPEchoAdminSourceAddress': '1.3.6.1.4.1.9.9.572.1.1.1.4',
    }

    STAT = {
        'rttMonLatestRttOperCompletionTime': '1.3.6.1.4.1.9.9.42.1.2.10.1.1',
        'rttMonLatestRttOperTime': '1.3.6.1.4.1.9.9.42.1.2.10.1.5',
        'rttMonLatestJitterOperNumOfRtt': '1.3.6.1.4.1.9.9.42.1.5.2.1.1',
        'rttMonLatestJitterOperRTTMin': '1.3.6.1.4.1.9.9.42.1.5.2.1.4',
        'rttMonLatestJitterOperRTTMax': '1.3.6.1.4.1.9.9.42.1.5.2.1.5',
        'rttMonLatestJitterOperPacketLossSD': '1.3.6.1.4.1.9.9.42.1.5.2.1.26',
    }

    CONVERSION = {
        'rttMonCtrlAdminRttType': {
            1: 'echo',
            2: 'pathEcho',
            3: 'fileIO',
            4: 'script',
            5: 'udpEcho',
            6: 'tcpConnect',
            7: 'http',
            8: 'dns',
            9: 'jitter',
            10: ':dlsw',
            11: ':dhcp',
            12: ':ftp',
            13: ':voip',
            14: ':rtp',
            15: ':lspGroup',
            16: ':icmpjitter',
            17: ':lspPing',
            18: ':lspTrace',
            19: ':ethernetPing',
            20: ':ethernetJitter',
            21: ':lspPingPseudowire',
            22: ':video',
            23: ':y1731Delay',
            24: ':y1731Loss',
            25: ':mcastJitter',
            26: ':fabricPathEcho',
        },
        'rttMonCtrlAdminStatus': {
            1: 'active',
            2: 'notInService',
            3: 'notReady',
            4: 'createAndGo',
            5: 'createAndWait',
            6: 'destroy',
        },
        'rttMonLatestRttOperSense': {
            0: 'other',
            1: 'ok',
            2: 'disconnected',
            3: 'overThreshold',
            4: 'timeout',
            5: 'busy',
            6: 'notConnected',
            7: 'dropped',
            8: 'sequenceError',
            9: 'verifyError',
            10: 'applicationSpecific',
            11: 'dnsServerTimeout',
            12: 'tcpConnectTimeout',
            13: 'httpTransactionTimeout',
            14: 'dnsQueryError',
            15: 'httpError',
            16: 'error',
            17: 'mplsLspEchoTxError',
            18: 'mplsLspUnreachable',
            19: 'mplsLspMalformedReq',
            20: 'mplsLspReachButNotFEC',
            21: 'enableOk',
            22: 'enableNoConnect',
            23: 'enableVersionFail',
            24: 'enableInternalError',
            25: 'enableAbort',
            26: 'enableFail',
            27: 'enableAuthFail',
            28: 'enableFormatError',
            29: 'enablePortInUse',
            30: 'statsRetrieveOk',
            31: 'statsRetrieveNoConnect',
            32: 'statsRetrieveVersionFail',
            33: 'statsRetrieveInternalError',
            34: 'statsRetrieveAbort',
            35: 'statsRetrieveFail',
            36: 'statsRetrieveAuthFail',
            37: 'statsRetrieveFormatError',
            38: 'statsRetrievePortInUse',
        },
        'crttMonIPEchoAdminTargetAddrType': {
            0: 'unknown',
            1: 'ipv4',
            2: 'ipv6',
            3: 'ipv4z',
            4: 'ipv6z',
            16: 'dns',
        },
        'crttMonIPEchoAdminSourceAddrType': {
            0: 'unknown',
            1: 'ipv4',
            2: 'ipv6',
            3: 'ipv4z',
            4: 'ipv6z',
            16: 'dns',
        },
    }

    XLATE = { }

    SNMP_QUERY_CHUNKS = 1

    def __init__(self, snmp):
        self.snmp = snmp
        self.data = dict()
        t = Timer("snmp inspect %s %s" % (CiscoRttMon.NAME, snmp.host))
        t.start_timer()
        super(CiscoRttMon, self).__init__(snmp)
        if CiscoDevice.BASE_OID not in str(self.sysObjectID):
            logging.debug("skipping cbqos check on non-cisco device %s", self.sysName)
            return None
        logging.info("inspecting %s for cisco rttmon data", snmp.host)
        self.data = self._get_configuration()
        t.stop_timer()

    def _get_configuration(self):
        ''' get cbqos objects '''
        data = dict()
        attrs = netspryte.snmp.get_snmp_data(self.snmp, self, CiscoRttMon.NAME, CiscoRttMon.ATTRS, CiscoRttMon.CONVERSION, CiscoRttMon.SNMP_QUERY_CHUNKS)
        metrics = netspryte.snmp.get_snmp_data(self.snmp, self, CiscoRttMon.NAME, CiscoRttMon.STAT, CiscoRttMon.CONVERSION, CiscoRttMon.SNMP_QUERY_CHUNKS)
        for k, v in list(attrs.items()):
            admin_tag = attrs[k].get('rttMonCtrlAdminTag', 'NA')
            title = "{0}:{1}".format(k, admin_tag)
            data[k] = self.initialize_instance(CiscoRttMon.NAME, k)
            data[k]['attrs'] = v
            data[k]['presentation'] = {'title': title, 'description': "NA"}
            if k in metrics:
                data[k]['metrics'] = metrics[k]
        return data
