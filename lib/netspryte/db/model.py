# Written by Stephen Fromm <stephenf nero net>
# (C) 2016 University of Oregon
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
import os
import logging
import subprocess

from netspryte import constants as C

from peewee import *
from playhouse.postgres_ext import *

DB_PROXY = Proxy()

class BaseModel(Model):
    class Meta:
        database = DB_PROXY

class Host(BaseModel):
    name = CharField(index=True)
    lastseen = DateTimeField(default=datetime.datetime.now, index=True)
    interval = IntegerField(default=C.DEFAULT_INTERVAL)

    class Meta:
        db_table = 'host'
        order_by = ("name",)

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

class MeasurementInstance(BaseModel):
    name  = CharField(index=True, unique=True)
    index = CharField()
    attrs = BinaryJSONField(null=True)
    metrics = BinaryJSONField(null=True)
    presentation = BinaryJSONField(null=True)
    lastseen = DateTimeField(default=datetime.datetime.now, index=True)
    host   = ForeignKeyField(Host,
                             related_name='measurement_instances', null=False, on_delete='CASCADE')
    measurement_class = ForeignKeyField(MeasurementClass,
                                        related_name='measurement_instances', null=False, on_delete='CASCADE')

    class Meta:
        db_table = "measurement_instance"
        order_by = ("name",)
