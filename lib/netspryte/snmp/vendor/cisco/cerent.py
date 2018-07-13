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
from netspryte.snmp.host import HostSystem

class CiscoCerent(HostSystem):

    NAME = 'cerent'
    DESCRIPTION = 'Cisco Cerent OTN'
    BASE_OID = "1.3.6.1.4.1.3607"

    ATTRS = {
        'cMsDwdmIfConfigProtocol' : '1.3.6.1.4.1.3607.2.40.1.1.1.1',
        'cMsDwdmIfConfigDataRate' : '1.3.6.1.4.1.3607.2.40.1.1.1.2',
        'cMsDwdmIfConfigLoopback' : '1.3.6.1.4.1.3607.2.40.1.1.1.3',
        'cMsDwdmIfConfigWavelength' : '1.3.6.1.4.1.3607.2.40.1.1.1.4',
        'cMsDwdmIfConfigOtnStatus' : '1.3.6.1.4.1.3607.2.40.1.1.1.5',
        'cMsDwdmIfConfigFECStatus' : '1.3.6.1.4.1.3607.2.40.1.1.1.6',
        'cMsDwdmIfConfigFECMode' : '1.3.6.1.4.1.3607.2.40.1.1.1.10',
    }

    STAT = {
    }

    CONVERSION = {
        'cMsDwdmIfConfigProtocol' : {
            1 : "other",
            2 : "unknown",
            4 : "tenGigEth",
            5 : "fibreChOrOneGigEth",
            7 : "unframed",
            8 : "sonet",
            9 : "sdh",
            10 : "sysplexIscCompatibility",
            11 : "sysplexIscPeer",
            12 : "sysplexTimerEtr",
            13 : "sysplexTimerClo",
            14 : "fastEthernet",
            15 : "fddi",
        },
        'cMsDwdmIfConfigDataRate' : {
            10 : "passThru",
            20 : "stm1",
            30 : "stm4",
            40 : "stm16",
            50 : "stm64",
            60 : "gigE",
            70 : "tenGigE",
            80 : "fc",
            90 : "oneGfcFicon",
            100 : "twoGfcFiconIsc3",
            110 : "escon",
            120 : "dv6000",
            130 : "sdiD1Video",
            140 : "hdtv",
            150 : "oc3",
            160 : "oc12",
            170 : "oc48",
            180 : "oc192",
            190 : "fourGfcFicon",
            200 : "tenGfc",
            210 : "isc1",
            220 : "isc3",
            230 : "oneGigIsc3",
            240 : "twoGigIsc3",
            250 : "etrClo",
        },
        'cMsDwdmIfConfigLoopback' : {
            1 : "noLoop",
            2 : "diagnosticLoop",
            3 : "lineLoop",
            4 : "otherLoop",
        },
        'cMsDwdmIfConfigWavelength' : {
            1 : "unknown",
            3 : "wv1529d55",
            4 : "wv1529d94",
            5 : "wv1530d33",
            7 : "wv1530d72",
            10 : "wv1531d12",
            12 : "wv1531d51",
            15 : "wv1531d90",
            17 : "wv1532d29",
            20 : "wv1532d68",
            22 : "wv1533d07",
            23 : "wv1533d47",
            24 : "wv1533d86",
            25 : "wv1534d25",
            27 : "wv1534d64",
            30 : "wv1535d04",
            32 : "wv1535d43",
            35 : "wv1535d82",
            37 : "wv1536d22",
            40 : "wv1536d61",
            42 : "wv1537d00",
            43 : "wv1537d40",
            44 : "wv1537d79",
            45 : "wv1538d19",
            47 : "wv1538d58",
            50 : "wv1538d98",
            52 : "wv1539d37",
            55 : "wv1539d77",
            57 : "wv1540d16",
            60 : "wv1540d56",
            62 : "wv1540d95",
            63 : "wv1541d35",
            64 : "wv1541d75",
            65 : "wv1542d14",
            67 : "wv1542d54",
            70 : "wv1542d94",
            72 : "wv1543d33",
            75 : "wv1543d73",
            77 : "wv1544d13",
            80 : "wv1544d53",
            82 : "wv1544d92",
            83 : "wv1545d32",
            84 : "wv1545d72",
            85 : "wv1546d12",
            87 : "wv1546d52",
            90 : "wv1546d92",
            92 : "wv1547d32",
            95 : "wv1547d72",
            97 : "wv1548d11",
            100 : "wv1548d51",
            102 : "wv1548d91",
            103 : "wv1549d32",
            104 : "wv1549d72",
            105 : "wv1550d12",
            107 : "wv1550d52",
            110 : "wv1550d92",
            112 : "wv1551d32",
            115 : "wv1551d72",
            117 : "wv1552d12",
            120 : "wv1552d52",
            122 : "wv1552d93",
            123 : "wv1553d33",
            124 : "wv1553d73",
            125 : "wv1554d13",
            127 : "wv1554d54",
            130 : "wv1554d94",
            132 : "wv1555d34",
            135 : "wv1555d75",
            137 : "wv1556d15",
            140 : "wv1556d55",
            142 : "wv1556d96",
            143 : "wv1557d36",
            144 : "wv1557d77",
            145 : "wv1558d17",
            147 : "wv1558d58",
            150 : "wv1558d98",
            152 : "wv1559d39",
            155 : "wv1559d79",
            157 : "wv1560d20",
            160 : "wv1560d61",
            162 : "wv1561d01",
            164 : "wv1561d42",
            166 : "wv1561d83",
            168 : "wv1570d83",
            170 : "wv1571d24",
            172 : "wv1571d65",
            174 : "wv1572d06",
            176 : "wv1572d48",
            178 : "wv1572d89",
            180 : "wv1573d30",
            182 : "wv1573d71",
            184 : "wv1574d13",
            186 : "wv1574d54",
            188 : "wv1574d95",
            190 : "wv1575d37",
            192 : "wv1575d78",
            194 : "wv1576d20",
            196 : "wv1576d61",
            198 : "wv1577d03",
            200 : "wv1577d44",
            205 : "wv1577d86",
            210 : "wv1578d27",
            215 : "wv1578d69",
            220 : "wv1579d10",
            225 : "wv1579d52",
            230 : "wv1579d93",
            235 : "wv1580d35",
            240 : "wv1580d77",
            245 : "wv1581d18",
            250 : "wv1581d60",
            255 : "wv1582d02",
            260 : "wv1582d44",
            265 : "wv1582d85",
            270 : "wv1583d27",
            275 : "wv1583d69",
            280 : "wv1584d11",
            285 : "wv1584d53",
            290 : "wv1584d95",
            295 : "wv1585d36",
            300 : "wv1585d78",
            305 : "wv1586d20",
            310 : "wv1586d62",
            315 : "wv1587d04",
            320 : "wv1587d46",
            325 : "wv1587d88",
            330 : "wv1588d30",
            335 : "wv1588d73",
            340 : "wv1589d15",
            345 : "wv1589d57",
            350 : "wv1589d99",
            355 : "wv1590d41",
            360 : "wv1590d83",
            365 : "wv1591d26",
            370 : "wv1591d68",
            375 : "wv1592d10",
            380 : "wv1592d52",
            385 : "wv1592d95",
            390 : "wv1593d37",
            395 : "wv1593d79",
            400 : "wv1594d22",
            405 : "wv1594d64",
            410 : "wv1595d06",
            415 : "wv1595d49",
            420 : "wv1595d91",
            425 : "wv1596d34",
            430 : "wv1596d76",
            435 : "wv1597d19",
            440 : "wv1597d62",
            445 : "wv1598d04",
            450 : "wv1598d47",
            455 : "wv1598d89",
            460 : "wv1599d32",
            465 : "wv1599d75",
            470 : "wv1600d17",
            475 : "wv1600d60",
            480 : "wv1601d03",
            485 : "wv1601d46",
            490 : "wv1601d88",
            500 : "wv1602d31",
            505 : "wv1602d74",
            510 : "wv1603d17",
            515 : "wv1603d60",
            520 : "wv1604d03",
        },
        'cMsDwdmIfConfigOthStatus' : {
            1 : "true",
            2 : "false",
        },
        'cMsDwdmIfConfigFECStatus' : {
            1 : "true",
            2 : "false",
        },
        'cMsDwdmIfConfigFECMode' : {
            1 : "disable",
            2 : "enableStandard",
            3 : "enableEnhanced",
        },
    }

    def __init__(self, snmp):
        self.snmp = snmp
        self.data = dict()
        super(CiscoCerent, self).__init__(snmp)
        if CiscoCerent.BASE_OID in str(self.sysObjectID):
            logging.info("inspecting %s for cerent data", snmp.host)
            self.data = self._get_configuration()
            logging.info("done inspecting %s for cerent data", snmp.host)

    def _get_configuration(self):
        data = dict()
        attrs = netspryte.snmp.get_snmp_data(self.snmp, self, CiscoCerent.NAME, CiscoCerent.ATTRS, CiscoCerent.CONVERSION)
        for k, v in attrs.items():
            data[k] = self.initialize_instance(CiscoCerent.NAME, k)
            data[k]['attrs'] = v
        return data
