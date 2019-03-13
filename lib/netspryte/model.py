# Written by Stephen Fromm <stephenf nero net>
# Copyright (C) 2016-2017 University of Oregon
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

import datetime

from netspryte import constants as C

from peewee import BigIntegerField, IntegerField, CharField, DateTimeField, ForeignKeyField, TextField, Proxy, Model
from playhouse.postgres_ext import BinaryJSONField


DB_PROXY = Proxy()


class BaseModel(Model):
    class Meta:
        database = DB_PROXY


class Netspryte(BaseModel):
    schema = IntegerField(default=1)

    class Meta:
        db_table = 'netspryte'


class Host(BaseModel):
    name = CharField(index=True)
    lastseen = DateTimeField(default=datetime.datetime.now, index=True)
    interval = IntegerField(default=C.DEFAULT_INTERVAL)

    class Meta:
        db_table = 'host'
        order_by = ("name",)

    def __repr__(self):
        return '<Host: %s>' % self.name

    def __str__(self):
        return '<Host: %s>' % self.name


class HostSnmpAttrs(BaseModel):
    sysDescr = CharField(null=True)
    sysObjectID = CharField()
    sysUpTime = BigIntegerField(null=True)
    sysContact = CharField(null=True)
    sysName = CharField()
    sysLocation = CharField(null=True)
    sysServices = CharField(null=True)
    host = ForeignKeyField(Host, related_name='host_snmp_attrs', null=False, on_delete='CASCADE')

    class Meta:
        db_table = 'host_snmp_attrs'

    def __repr__(self):
        return '<HostSnmpAttrs: %s>' % self.sysName

    def __str__(self):
        return '<HostSnmpAttrs: %s>' % self.sysName


class MeasurementClass(BaseModel):
    name = CharField()
    description = CharField(null=True)
    transport = CharField()
    metric_type = BinaryJSONField(index=True, null=True)

    class Meta:
        db_table = "measurement_class"
        order_by = ("name", "transport",)
        indexes = (
            (('name', 'transport'), True),
        )

    def __repr__(self):
        return '<MeasurementClass: %s>' % self.name

    def __str__(self):
        return '<MeasurementClass: %s>' % self.name


class MeasurementInstance(BaseModel):
    name = CharField(index=True, unique=True)
    index = CharField()
    presentation = BinaryJSONField(null=True)
    lastseen = DateTimeField(default=datetime.datetime.now, index=True)
    host = ForeignKeyField(Host, related_name='measurement_instances', null=False, on_delete='CASCADE')
    measurement_class = ForeignKeyField(MeasurementClass, related_name='measurement_instances', null=False, on_delete='CASCADE')

    class Meta:
        db_table = "measurement_instance"
        order_by = ("name",)

    def __repr__(self):
        return '<MeasurementInstance: %s>' % self.name

    def __str__(self):
        return '<MeasurementInstance: %s>' % self.name


class Tag(BaseModel):
    name = CharField()

    class Meta:
        db_table = "tag"

    def __repr__(self):
        return '<Tag: %s>' % self.name


class MeasurementInstanceTag(BaseModel):
    measurement_instance = ForeignKeyField(MeasurementInstance, backref='tags')
    tag = ForeignKeyField(Tag, backref='measurementinstances')

    class Meta:
        db_table = "measurement_instance_tag"


class HostTag(BaseModel):
    host = ForeignKeyField(Host, backref='tags')
    tag = ForeignKeyField(Tag, backref='hosts')

    class Meta:
        db_table = "host_tag"


class IPAddressAttrs(BaseModel):
    """
    A PeeWee model for a IP Network
    """

    ipAddressAddrType = CharField(null=True)
    ipAddressAddr = CharField()
    ipAddressIfIndex = IntegerField(null=True)
    ipAddressType = CharField(null=True)
    ipAddressPrefix = CharField(null=True)
    ipAddressOrigin = CharField(null=True)
    ipAddressStatus = CharField(null=True)
    measurement_instance = ForeignKeyField(MeasurementInstance, related_name='ipaddress_attrs', null=False, on_delete='CASCADE')

    class Meta:
        db_table = "ipaddress_attrs"

    def __repr__(self):
        return '<IPAddressAttrs: %s>' % (self.ipAddressAddr)

    def __str__(self):
        return '<IPAddressAttrs: %s>' % (self.ipAddressAddr)


class InterfaceAttrs(BaseModel):
    ifIndex = IntegerField()
    ifDescr = CharField(null=True)
    ifType = IntegerField(null=True)
    ifMtu = IntegerField(null=True)
    ifSpeed = BigIntegerField(null=True)
    ifPhysAddress = CharField(null=True)
    ifAdminStatus = CharField(null=True)
    ifOperStatus = CharField(null=True)
    ifName = CharField(null=True)
    ifHighSpeed = IntegerField(null=True)
    ifAlias = TextField(null=True)
    measurement_instance = ForeignKeyField(MeasurementInstance, related_name='interface_attrs', null=False, on_delete='CASCADE')

    class Meta:
        db_table = "interface_attrs"

    def __repr__(self):
        return '<InterfaceAttrs: %s:%s>' % (self.ifIndex, self.ifName)

    def __str__(self):
        return '<InterfaceAttrs: %s:%s>' % (self.ifIndex, self.ifName)


class InterfaceMetrics(BaseModel):
    ifInNUcastPkts = BigIntegerField(null=True)
    ifInDiscards = BigIntegerField(null=True)
    ifInErrors = BigIntegerField(null=True)
    ifInUnknownProtos = BigIntegerField(null=True)
    ifOutNUcastPkts = BigIntegerField(null=True)
    ifOutDiscards = BigIntegerField(null=True)
    ifOutErrors = BigIntegerField(null=True)
    ifOutQLen = BigIntegerField(null=True)
    ifInMulticastPkts = BigIntegerField(null=True)
    ifInBroadcastPkts = BigIntegerField(null=True)
    ifOutMulticastPkts = BigIntegerField(null=True)
    ifOutBroadcastPkts = BigIntegerField(null=True)
    ifHCInOctets = BigIntegerField(null=True)
    ifHCInUcastPkts = BigIntegerField(null=True)
    ifHCInMulticastPkts = BigIntegerField(null=True)
    ifHCInBroadcastPkts = BigIntegerField(null=True)
    ifHCOutOctets = BigIntegerField(null=True)
    ifHCOutUcastPkts = BigIntegerField(null=True)
    ifHCOutMulticastPkts = BigIntegerField(null=True)
    ifHCOutBroadcastPkts = BigIntegerField(null=True)
    timestamp = DateTimeField(default=datetime.datetime.now, index=True)
    measurement_instance = ForeignKeyField(MeasurementInstance, related_name='interface_metrics', null=False, on_delete='CASCADE')

    class Meta:
        db_table = "interface_metrics"

    def __repr__(self):
        return '<InterfaceMetrics: %s>' % (self.measurement_instance)

    def __str__(self):
        return '<InterfaceMetrics: %s>' % (self.measurement_instance)


class UPSAttrs(BaseModel):
    upsIdentManufacturer = CharField()
    upsIdentModel = CharField()
    upsIdentUPSSoftwareVersion = CharField()
    upsIdentAgentSoftwareVersion = CharField()
    upsIdentName = CharField()
    upsIdentAttachedDevices = CharField()
    upsInputNumLines = CharField()
    upsOutputSource = CharField()
    upsOutputFrequency = IntegerField()
    upsOutputNumLines = CharField()
    measurement_instance = ForeignKeyField(MeasurementInstance, related_name='hostups_attrs', null=False, on_delete='CASCADE')

    class Meta:
        db_table = "hostups_attrs"

    def __repr__(self):
        return '<UPSAttrs: %s>' % self.upsIdentName

    def __str__(self):
        return '<UPSAttrs: %s>' % self.upsIdentName


class UPSMetrics(BaseModel):
    upsBatteryStatus = BigIntegerField(null=True)
    upsSecondsOnBattery = BigIntegerField(null=True)
    upsEstimatedMinutesRemaining = BigIntegerField(null=True)
    upsEstimatedChargeRemaining = BigIntegerField(null=True)
    upsBatteryVoltage = BigIntegerField(null=True)
    upsBatteryCurrent = BigIntegerField(null=True)
    upsBatteryTemperature = BigIntegerField(null=True)
    upsInputLineBads = BigIntegerField(null=True)
    upsInputFrequency = BigIntegerField(null=True)
    upsInputVoltage = BigIntegerField(null=True)
    upsInputCurrent = BigIntegerField(null=True)
    upsInputTruePower = BigIntegerField(null=True)
    upsOutputVoltage = BigIntegerField(null=True)
    upsOutputCurrent = BigIntegerField(null=True)
    upsOutputPower = BigIntegerField(null=True)
    upsOutputPercentLoad = BigIntegerField(null=True)
    timestamp = DateTimeField(default=datetime.datetime.now, index=True)
    measurement_instance = ForeignKeyField(MeasurementInstance, related_name='hostups_metrics', null=False, on_delete='CASCADE')

    class Meta:
        db_table = "hostups_metrics"

    def __repr__(self):
        return '<UPSMetrics: %s>' % self.measurement_instance

    def __str__(self):
        return '<UPSMetrics: %s>' % self.measurement_instance


class CBQOSAttrs(BaseModel):
    cbQosIfType = CharField(null=True)
    cbQosPolicyDirection = CharField(null=True)
    cbQosIfIndex = IntegerField()
    cbQosConfigIndex = CharField(null=True)
    cbQosObjectsType = CharField()
    cbQosParentObjectsIndex = CharField(null=True)
    cbQosPolicyMapName = CharField(null=True)
    cbQosCMName = CharField(null=True)
    cbQosPoliceCfgBurstSize = IntegerField(null=True)
    cbQosPoliceCfgExtBurstSize = CharField(null=True)
    cbQosPoliceCfgConformAction = CharField(null=True)
    cbQosPoliceCfgExceedAction = CharField(null=True)
    cbQosPoliceCfgViolateAction = CharField(null=True)
    cbQosPoliceCfgRate64 = BigIntegerField(null=True)
    measurement_instance = ForeignKeyField(MeasurementInstance, related_name='cbqos_attrs', null=False, on_delete='CASCADE')

    class Meta:
        db_table = "cbqos_attrs"

    def __repr__(self):
        return '<CBQOSAttrs: %s>' % self.cbQosConfigIndex

    def __str__(self):
        return '<CBQOSAttrs: %s>' % self.cbQosConfigIndex


class CBQOSMetrics(BaseModel):
    cbQosPoliceConformedPkt64 = BigIntegerField(null=True)
    cbQosPoliceConformedByte64 = BigIntegerField(null=True)
    cbQosPoliceConformedBitRate = BigIntegerField(null=True)
    cbQosPoliceExceededPkt64 = BigIntegerField(null=True)
    cbQosPoliceExceededByte64 = BigIntegerField(null=True)
    cbQosPoliceExceededBitRate = BigIntegerField(null=True)
    cbQosPoliceViolatedPkt64 = BigIntegerField(null=True)
    cbQosPoliceViolatedByte64 = BigIntegerField(null=True)
    cbQosPoliceViolatedBitRate = BigIntegerField(null=True)
    timestamp = DateTimeField(default=datetime.datetime.now, index=True)
    measurement_instance = ForeignKeyField(MeasurementInstance, related_name='cbqos_metrics', null=False, on_delete='CASCADE')

    class Meta:
        db_table = "cbqos_metrics"

    def __repr__(self):
        return '<CBQOSMetrics: %s>' % self.measurement_instance

    def __str__(self):
        return '<CBQOSMetrics: %s>' % self.measurement_instance
