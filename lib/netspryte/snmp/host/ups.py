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

class HostUPS():

    NAME = 'ups'

    DATA = {
        'upsIdentManufacturer'         : '1.3.6.1.2.1.33.1.1.1',
        'upsIdentModel'                : '1.3.6.1.2.1.33.1.1.2',
        'upsIdentUPSSoftwareVersion'   : '1.3.6.1.2.1.33.1.1.3',
        'upsIdentAgentSoftwareVersion' : '1.3.6.1.2.1.33.1.1.4',
        'upsIdentName'                 : '1.3.6.1.2.1.33.1.1.5',
        'upsIdentAttachedDevices'      : '1.3.6.1.2.1.33.1.1.6',
        'upsInputNumLines'             : '1.3.6.1.2.1.33.1.3.2',
        'upsOutputSource'              : '1.3.6.1.2.1.33.1.4.1',
        'upsOutputFrequency'           : '1.3.6.1.2.1.33.1.4.2',
        'upsOutputNumLines'            : '1.3.6.1.2.1.33.1.4.3',
    }

    STAT = {
        'upsBatteryStatus'             : '1.3.6.1.2.1.33.1.2.1',
        'upsSecondsOnBattery'          : '1.3.6.1.2.1.33.1.2.2',
        'upsEstimatedMinutesRemaining' : '1.3.6.1.2.1.33.1.2.3',
        'upsEstimatedChargeRemaining'  : '1.3.6.1.2.1.33.1.2.4',
        'upsBatteryVoltage'            : '1.3.6.1.2.1.33.1.2.5',
        'upsBatteryCurrent'            : '1.3.6.1.2.1.33.1.2.6',
        'upsBatteryTemperature'        : '1.3.6.1.2.1.33.1.2.7',
        'upsInputLineBads'             : '1.3.6.1.2.1.33.1.3.1',
        'upsInputFrequency'            : '1.3.6.1.2.1.33.1.3.3.1.2',
        'upsInputVoltage'              : '1.3.6.1.2.1.33.1.3.3.1.3',
        'upsInputCurrent'              : '1.3.6.1.2.1.33.1.3.3.1.4',
        'upsInputTruePower'            : '1.3.6.1.2.1.33.1.3.3.1.5',
        'upsOutputVoltage'             : '1.3.6.1.2.1.33.1.4.4.1.2',
        'upsOutputCurrent'             : '1.3.6.1.2.1.33.1.4.4.1.3',
        'upsOutputPower'               : '1.3.6.1.2.1.33.1.4.4.1.4',
        'upsOutputPercentLoad'         : '1.3.6.1.2.1.33.1.4.4.1.5',
    }

    CONVERSION = {
        'upsBatteryStatus' : {
            1 : 'unknown',
            2 : 'batteryNormal',
            3 : 'batteryLow',
            4 : 'batteryDepleted',
        },
        'upsOutputSource' : {
            1 : "other",
            2 : "none",
            3 : "normal",
            4 : "bypass",
            5 : "battery",
            6 : "booster",
            7 : "reducer",
        },
    }

    def __init__(self, snmp):
        self.snmp = snmp
        self._ups = self._get_ups_data()
        self._ups = self._get_ups_stats()

    def _get_ups_data(self):
        return netspryte.snmp.get_snmp_data(self.snmp, HostUPS.NAME,
                                            HostUPS.DATA, HostUPS.CONVERSION)

    def _get_ups_stats(self):
        return netspryte.snmp.get_snmp_data(self.snmp,  HostUPS.NAME,
                                            HostUPS.STAT, HostUPS.CONVERSION)

    @property
    def ups(self):
        return self._ups

