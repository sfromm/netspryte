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

# A note on Field / Column types:
# BigIntegerField (bigint) is an 8 byte field with a range of -9223372036854775808 to 9223372036854775807.
# DecimalField (numeric) is variable sized, but supports up to 131072 digits before the decimal point.
# A SNMP Counter64 object is an unsigned 64 bit integer with a range of 0 to 18446744073709551615.
# This means any Counter64 SNMP field will overflow a BigIntegerField.
# That then requires the use of DecimalField(max_digits=21)
# For further reference, see:
#   https://www.postgresql.org/docs/current/datatype-numeric.html
#   http://docs.peewee-orm.com/en/latest/peewee/models.html#field-types-table
#   http://docs.peewee-orm.com/en/latest/peewee/api.html#DecimalField

import datetime

from netspryte import constants as C

from peewee import BigIntegerField, BooleanField, CharField, DateTimeField, ForeignKeyField, IntegerField, DecimalField, TextField, Proxy, Model
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
    host = ForeignKeyField(Host, backref='host_snmp_attrs', null=False, on_delete='CASCADE')

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
    has_metrics = BooleanField(default=False)
    host = ForeignKeyField(Host, backref='measurement_instances', null=False, on_delete='CASCADE')
    measurement_class = ForeignKeyField(MeasurementClass, backref='measurement_instances', null=False, on_delete='CASCADE')

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
    measurement_instance = ForeignKeyField(MeasurementInstance, backref='ipaddress_attrs', null=False, on_delete='CASCADE')

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
    measurement_instance = ForeignKeyField(MeasurementInstance, backref='interface_attrs', null=False, on_delete='CASCADE')

    class Meta:
        db_table = "interface_attrs"

    def __repr__(self):
        return '<InterfaceAttrs: %s:%s>' % (self.ifIndex, self.ifName)

    def __str__(self):
        return '<InterfaceAttrs: %s:%s>' % (self.ifIndex, self.ifName)


class InterfaceMetrics(BaseModel):
    ifInNUcastPkts = DecimalField(max_digits=20, decimal_places=0, null=True)
    ifInDiscards = DecimalField(max_digits=20, decimal_places=0, null=True)
    ifInErrors = DecimalField(max_digits=20, decimal_places=0, null=True)
    ifInUnknownProtos = DecimalField(max_digits=20, decimal_places=0, null=True)
    ifOutNUcastPkts = DecimalField(max_digits=20, decimal_places=0, null=True)
    ifOutDiscards = DecimalField(max_digits=20, decimal_places=0, null=True)
    ifOutErrors = DecimalField(max_digits=20, decimal_places=0, null=True)
    ifOutQLen = DecimalField(max_digits=20, decimal_places=0, null=True)
    ifInMulticastPkts = DecimalField(max_digits=20, decimal_places=0, null=True)
    ifInBroadcastPkts = DecimalField(max_digits=20, decimal_places=0, null=True)
    ifOutMulticastPkts = DecimalField(max_digits=20, decimal_places=0, null=True)
    ifOutBroadcastPkts = DecimalField(max_digits=20, decimal_places=0, null=True)
    ifHCInOctets = DecimalField(max_digits=20, decimal_places=0, null=True)
    ifHCInUcastPkts = DecimalField(max_digits=20, decimal_places=0, null=True)
    ifHCInMulticastPkts = DecimalField(max_digits=20, decimal_places=0, null=True)
    ifHCInBroadcastPkts = DecimalField(max_digits=20, decimal_places=0, null=True)
    ifHCOutOctets = DecimalField(max_digits=20, decimal_places=0, null=True)
    ifHCOutUcastPkts = DecimalField(max_digits=20, decimal_places=0, null=True)
    ifHCOutMulticastPkts = DecimalField(max_digits=20, decimal_places=0, null=True)
    ifHCOutBroadcastPkts = DecimalField(max_digits=20, decimal_places=0, null=True)
    timestamp = DateTimeField(default=datetime.datetime.now, index=True)
    measurement_instance = ForeignKeyField(MeasurementInstance, backref='interface_metrics', null=False, on_delete='CASCADE')

    class Meta:
        db_table = "interface_metrics"
        order_by = ("timestamp",)

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
    measurement_instance = ForeignKeyField(MeasurementInstance, backref='ups_attrs', null=False, on_delete='CASCADE')

    class Meta:
        db_table = "hostups_attrs"

    def __repr__(self):
        return '<UPSAttrs: %s>' % self.upsIdentName

    def __str__(self):
        return '<UPSAttrs: %s>' % self.upsIdentName


class UPSMetrics(BaseModel):
    upsBatteryStatus = DecimalField(max_digits=20, decimal_places=0, null=True)
    upsSecondsOnBattery = DecimalField(max_digits=20, decimal_places=0, null=True)
    upsEstimatedMinutesRemaining = DecimalField(max_digits=20, decimal_places=0, null=True)
    upsEstimatedChargeRemaining = DecimalField(max_digits=20, decimal_places=0, null=True)
    upsBatteryVoltage = DecimalField(max_digits=20, decimal_places=0, null=True)
    upsBatteryCurrent = DecimalField(max_digits=20, decimal_places=0, null=True)
    upsBatteryTemperature = DecimalField(max_digits=20, decimal_places=0, null=True)
    upsInputLineBads = DecimalField(max_digits=20, decimal_places=0, null=True)
    upsInputFrequency = DecimalField(max_digits=20, decimal_places=0, null=True)
    upsInputVoltage = DecimalField(max_digits=20, decimal_places=0, null=True)
    upsInputCurrent = DecimalField(max_digits=20, decimal_places=0, null=True)
    upsInputTruePower = DecimalField(max_digits=20, decimal_places=0, null=True)
    upsOutputVoltage = DecimalField(max_digits=20, decimal_places=0, null=True)
    upsOutputCurrent = DecimalField(max_digits=20, decimal_places=0, null=True)
    upsOutputPower = DecimalField(max_digits=20, decimal_places=0, null=True)
    upsOutputPercentLoad = DecimalField(max_digits=20, decimal_places=0, null=True)
    timestamp = DateTimeField(default=datetime.datetime.now, index=True)
    measurement_instance = ForeignKeyField(MeasurementInstance, backref='ups_metrics', null=False, on_delete='CASCADE')

    class Meta:
        db_table = "hostups_metrics"
        order_by = ("timestamp",)

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
    cbQosPoliceCfgRate64 = DecimalField(max_digits=20, decimal_places=0, null=True)
    measurement_instance = ForeignKeyField(MeasurementInstance, backref='cbqos_attrs', null=False, on_delete='CASCADE')

    class Meta:
        db_table = "cbqos_attrs"

    def __repr__(self):
        return '<CBQOSAttrs: %s>' % self.cbQosConfigIndex

    def __str__(self):
        return '<CBQOSAttrs: %s>' % self.cbQosConfigIndex


class CBQOSMetrics(BaseModel):
    cbQosPoliceConformedPkt64 = DecimalField(max_digits=20, decimal_places=0, null=True)
    cbQosPoliceConformedByte64 = DecimalField(max_digits=20, decimal_places=0, null=True)
    cbQosPoliceConformedBitRate = DecimalField(max_digits=20, decimal_places=0, null=True)
    cbQosPoliceExceededPkt64 = DecimalField(max_digits=20, decimal_places=0, null=True)
    cbQosPoliceExceededByte64 = DecimalField(max_digits=20, decimal_places=0, null=True)
    cbQosPoliceExceededBitRate = DecimalField(max_digits=20, decimal_places=0, null=True)
    cbQosPoliceViolatedPkt64 = DecimalField(max_digits=20, decimal_places=0, null=True)
    cbQosPoliceViolatedByte64 = DecimalField(max_digits=20, decimal_places=0, null=True)
    cbQosPoliceViolatedBitRate = DecimalField(max_digits=20, decimal_places=0, null=True)
    timestamp = DateTimeField(default=datetime.datetime.now, index=True)
    measurement_instance = ForeignKeyField(MeasurementInstance, backref='cbqos_metrics', null=False, on_delete='CASCADE')

    class Meta:
        db_table = "cbqos_metrics"
        order_by = ("timestamp",)

    def __repr__(self):
        return '<CBQOSMetrics: %s>' % self.measurement_instance

    def __str__(self):
        return '<CBQOSMetrics: %s>' % self.measurement_instance
