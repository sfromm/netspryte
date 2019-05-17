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
    sysdescr = CharField(null=True)
    sysobjectid = CharField()
    sysuptime = BigIntegerField(null=True)
    syscontact = CharField(null=True)
    sysname = CharField()
    syslocation = CharField(null=True)
    sysservices = CharField(null=True)
    host = ForeignKeyField(Host, backref='host_snmp_attrs', null=False, on_delete='CASCADE')

    class Meta:
        db_table = 'host_snmp_attrs'

    def __repr__(self):
        return '<HostSnmpAttrs: %s>' % self.sysname

    def __str__(self):
        return '<HostSnmpAttrs: %s>' % self.sysname


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
    name = TextField(index=True, unique=True)
    title = CharField(null=True)
    description = CharField(null=True)
    index = TextField()
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


class Relationship(BaseModel):
    from_measurement_instance = ForeignKeyField(MeasurementInstance, backref='relationships')
    to_measurement_instance = ForeignKeyField(MeasurementInstance, backref='related_to')

    class Meta:
        db_table = "relationship"

    def __repr__(self):
        return '<RelatedMeasurementInstanceTag: %s>' % self.id

    def __str__(self):
        return '<RelatedMeasurementInstanceTag: %s>' % self.id


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

    addresstype = CharField(null=True)
    ipaddress = CharField()
    ifindex = IntegerField(null=True)
    ipaddresstype = CharField(null=True)
    prefix = CharField(null=True)
    origin = CharField(null=True)
    status = CharField(null=True)
    measurement_instance = ForeignKeyField(MeasurementInstance, backref='ipaddress_attrs', null=False, on_delete='CASCADE')

    class Meta:
        db_table = "ipaddress_attrs"

    def __repr__(self):
        return '<IPAddressAttrs: %s>' % (self.ipaddress)

    def __str__(self):
        return '<IPAddressAttrs: %s>' % (self.ipaddress)


class InterfaceAttrs(BaseModel):
    ifindex = IntegerField()
    ifdescr = CharField(null=True)
    iftype = IntegerField(null=True)
    ifmtu = IntegerField(null=True)
    ifspeed = BigIntegerField(null=True)
    ifphysaddress = CharField(null=True)
    ifadminstatus = CharField(null=True)
    ifoperstatus = CharField(null=True)
    ifname = CharField(null=True)
    ifhighspeed = IntegerField(null=True)
    ifalias = TextField(null=True)
    measurement_instance = ForeignKeyField(MeasurementInstance, backref='interface_attrs', null=False, on_delete='CASCADE')

    class Meta:
        db_table = "interface_attrs"

    def __repr__(self):
        return '<InterfaceAttrs: %s:%s>' % (self.ifindex, self.ifname)

    def __str__(self):
        return '<InterfaceAttrs: %s:%s>' % (self.ifindex, self.ifname)


class InterfaceMetrics(BaseModel):
    innucastpkts = DecimalField(max_digits=20, decimal_places=0, null=True)
    indiscards = DecimalField(max_digits=20, decimal_places=0, null=True)
    inerrors = DecimalField(max_digits=20, decimal_places=0, null=True)
    inunknownprotos = DecimalField(max_digits=20, decimal_places=0, null=True)
    outnucastpkts = DecimalField(max_digits=20, decimal_places=0, null=True)
    outdiscards = DecimalField(max_digits=20, decimal_places=0, null=True)
    outerrors = DecimalField(max_digits=20, decimal_places=0, null=True)
    outqlen = DecimalField(max_digits=20, decimal_places=0, null=True)
    inoctets = DecimalField(max_digits=20, decimal_places=0, null=True)
    inucastpkts = DecimalField(max_digits=20, decimal_places=0, null=True)
    inmulticastpkts = DecimalField(max_digits=20, decimal_places=0, null=True)
    inbroadcastpkts = DecimalField(max_digits=20, decimal_places=0, null=True)
    outoctets = DecimalField(max_digits=20, decimal_places=0, null=True)
    outucastpkts = DecimalField(max_digits=20, decimal_places=0, null=True)
    outmulticastpkts = DecimalField(max_digits=20, decimal_places=0, null=True)
    outbroadcastpkts = DecimalField(max_digits=20, decimal_places=0, null=True)
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
    upsidentmanufacturer = CharField()
    upsidentmodel = CharField()
    upsidentupssoftwareversion = CharField()
    upsidentagentsoftwareversion = CharField()
    upsidentname = CharField()
    upsidentattacheddevices = CharField()
    upsinputnumlines = CharField()
    upsoutputsource = CharField()
    upsoutputfrequency = IntegerField()
    upsoutputnumlines = CharField()
    measurement_instance = ForeignKeyField(MeasurementInstance, backref='ups_attrs', null=False, on_delete='CASCADE')

    class Meta:
        db_table = "hostups_attrs"

    def __repr__(self):
        return '<UPSAttrs: %s>' % self.upsidentname

    def __str__(self):
        return '<UPSAttrs: %s>' % self.upsidentname


class UPSMetrics(BaseModel):
    upsbatterystatus = DecimalField(max_digits=20, decimal_places=0, null=True)
    upssecondsonbattery = DecimalField(max_digits=20, decimal_places=0, null=True)
    upsestimatedminutesremaining = DecimalField(max_digits=20, decimal_places=0, null=True)
    upsestimatedchargeremaining = DecimalField(max_digits=20, decimal_places=0, null=True)
    upsbatteryvoltage = DecimalField(max_digits=20, decimal_places=0, null=True)
    upsbatterycurrent = DecimalField(max_digits=20, decimal_places=0, null=True)
    upsbatterytemperature = DecimalField(max_digits=20, decimal_places=0, null=True)
    inputlinebads = DecimalField(max_digits=20, decimal_places=0, null=True)
    inputfrequency = DecimalField(max_digits=20, decimal_places=0, null=True)
    inputvoltage = DecimalField(max_digits=20, decimal_places=0, null=True)
    inputcurrent = DecimalField(max_digits=20, decimal_places=0, null=True)
    inputtruepower = DecimalField(max_digits=20, decimal_places=0, null=True)
    outputvoltage = DecimalField(max_digits=20, decimal_places=0, null=True)
    outputcurrent = DecimalField(max_digits=20, decimal_places=0, null=True)
    outputpower = DecimalField(max_digits=20, decimal_places=0, null=True)
    outputpercentload = DecimalField(max_digits=20, decimal_places=0, null=True)
    timestamp = DateTimeField(default=datetime.datetime.now, index=True)
    measurement_instance = ForeignKeyField(MeasurementInstance, backref='ups_metrics', null=False, on_delete='CASCADE')

    class Meta:
        db_table = "hostups_metrics"
        order_by = ("timestamp",)

    def __repr__(self):
        return '<UPSMetrics: %s>' % self.measurement_instance

    def __str__(self):
        return '<UPSMetrics: %s>' % self.measurement_instance


class QOSAttrs(BaseModel):
    policydirection = CharField(null=True)
    ifindex = IntegerField()
    configindex = CharField(null=True)
    objectstype = CharField()
    policymapname = CharField(null=True)
    cmname = CharField(null=True)
    policecfgrate = DecimalField(max_digits=20, decimal_places=0, null=True)
    measurement_instance = ForeignKeyField(MeasurementInstance, backref='qos_attrs', null=False, on_delete='CASCADE')

    class Meta:
        db_table = "qos_attrs"

    def __repr__(self):
        return '<QOSAttrs: %s>' % self.policymapname

    def __str__(self):
        return '<QOSAttrs: %s>' % self.policymapname


class QOSMetrics(BaseModel):
    prepolicypkts = DecimalField(max_digits=20, decimal_places=0, null=True)
    prepolicybyte = DecimalField(max_digits=20, decimal_places=0, null=True)
    postpolicypkts = DecimalField(max_digits=20, decimal_places=0, null=True)
    postpolicybyte = DecimalField(max_digits=20, decimal_places=0, null=True)
    droppkts = DecimalField(max_digits=20, decimal_places=0, null=True)
    dropbyte = DecimalField(max_digits=20, decimal_places=0, null=True)
    timestamp = DateTimeField(default=datetime.datetime.now, index=True)
    measurement_instance = ForeignKeyField(MeasurementInstance, backref='qos_metrics', null=False, on_delete='CASCADE')

    class Meta:
        db_table = "qos_metrics"
        order_by = ("timestamp",)

    def __repr__(self):
        return '<QOSMetrics: %s>' % self.measurement_instance

    def __str__(self):
        return '<QOSMetrics: %s>' % self.measurement_instance
