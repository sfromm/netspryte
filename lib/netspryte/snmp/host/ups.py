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


class HostUPS(HostSystem):

    NAME = 'ups'
    DESCRIPTION = 'UPS'
    ATTR_MODEL = "UPSAttrs"
    METRIC_MODEL = "UPSMetrics"

    ATTRS = {
        'upsidentmanufacturer': '1.3.6.1.2.1.33.1.1.1',
        'upsidentmodel': '1.3.6.1.2.1.33.1.1.2',
        'upsidentupssoftwareversion': '1.3.6.1.2.1.33.1.1.3',
        'upsidentagentsoftwareversion': '1.3.6.1.2.1.33.1.1.4',
        'upsidentname': '1.3.6.1.2.1.33.1.1.5',
        'upsidentattacheddevices': '1.3.6.1.2.1.33.1.1.6',
        'upsinputnumlines': '1.3.6.1.2.1.33.1.3.2',
        'upsoutputsource': '1.3.6.1.2.1.33.1.4.1',
        'upsoutputfrequency': '1.3.6.1.2.1.33.1.4.2',
        'upsoutputnumlines': '1.3.6.1.2.1.33.1.4.3',
    }

    STAT = {
        'upsbatterystatus': '1.3.6.1.2.1.33.1.2.1',
        'upssecondsonbattery': '1.3.6.1.2.1.33.1.2.2',
        'estimatedminutesremaining': '1.3.6.1.2.1.33.1.2.3',
        'estimatedchargeremaining': '1.3.6.1.2.1.33.1.2.4',
        'upsbatteryvoltage': '1.3.6.1.2.1.33.1.2.5',
        'upsbatterycurrent': '1.3.6.1.2.1.33.1.2.6',
        'upsbatterytemperature': '1.3.6.1.2.1.33.1.2.7',
        'inputlinebads': '1.3.6.1.2.1.33.1.3.1',
        'inputfrequency': '1.3.6.1.2.1.33.1.3.3.1.2',
        'inputvoltage': '1.3.6.1.2.1.33.1.3.3.1.3',
        'inputcurrent': '1.3.6.1.2.1.33.1.3.3.1.4',
        'inputtruepower': '1.3.6.1.2.1.33.1.3.3.1.5',
        'outputvoltage': '1.3.6.1.2.1.33.1.4.4.1.2',
        'outputcurrent': '1.3.6.1.2.1.33.1.4.4.1.3',
        'outputpower': '1.3.6.1.2.1.33.1.4.4.1.4',
        'outputpercentload': '1.3.6.1.2.1.33.1.4.4.1.5',
    }

    CONVERSION = {
        'upsbatterystatus': {
            1: 'unknown',
            2: 'batteryNormal',
            3: 'batteryLow',
            4: 'batteryDepleted',
        },
        'upsoutputsource': {
            1: "other",
            2: "none",
            3: "normal",
            4: "bypass",
            5: "battery",
            6: "booster",
            7: "reducer",
        },
    }

    def __init__(self, snmp):
        self.snmp = snmp
        super(HostUPS, self).__init__(snmp)
        self.data = self._get_ups_data()

    def _get_ups_data(self):
        data = dict()
        attrs = netspryte.snmp.get_snmp_data(self.snmp, self, HostUPS.NAME, HostUPS.ATTRS, HostUPS.CONVERSION)
        metrics = netspryte.snmp.get_snmp_data(self.snmp, self, HostUPS.NAME, HostUPS.STAT, HostUPS.CONVERSION)
        for k, v in list(attrs.items()):
            data[k] = self.initialize_instance(HostUPS.NAME, k)
            data[k]['attrs'] = v
            data[k]['metrics'] = metrics[k]
        return data
