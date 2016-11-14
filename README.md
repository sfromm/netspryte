netspryte
==========

*netspryte* is a library and set of utilities to query network equipment
and get structured data back that describes the device.

Installation
--------------

*Netspryte* has the following prerequisites:

* pysnmp
* jinja2

Depending on the backend you use, you will require:

* rrdtool
* influxdb

To install, you can build an rpm with:

``` shell
make rpm
yum install rpm-build/noarch/netspryte-*.rpm
```
