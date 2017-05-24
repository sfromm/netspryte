netspryte
==========

*netspryte* is a library and set of utilities to query network equipment
and get structured data back that describes the device.

Installation
---------------

*Netspryte* is intended to be deployed using containers.  The included
*docker-compoose.yml* file will launch three services:

* collector - This will poll devices and collect data.
* web - The web frontend.
* database - Where collected information is stored.  Note this is not
  the metrics themselves.

Before you start the services, you should look at the file
*netspryte.params* and consider where you want the measurement data to
be stored.  You should update the variables **CONTAINER_DATADIR** and
**CONTAINER_CONFIGDIR**.  The variable **CONTAINER_DATADIR** defines
what local path to use as a volume for where RRDs will be stored.  The
variable **CONTAINER_CONFIGDIR** defines the local path to use as a
volume for configuration data.

To start the services:

``` shell
make start
```

This will start all the services.  To stop:

``` shell
make stop
```

## Building containers

If you wish, you can build the containers yourself.  If you also choose
to push the images to *hub.docker.com*, be sure to update the variables
**COLLECTOR_IMAGE_NAME** and **WEB_IMAGE_NAME**.

To build the containers:

``` shell
make build
```

You can then optionally `make push` if you have defined a new image name
and tag.

Configuration
----------------

Review *netspryte.cfg* for what is configurable.  This is also where the
list of devices to poll is configured.

Once you have configured the list of devices to poll, it is time to
set up the collector to poll your devices.  This can be done with:

``` shell
make cron-add
```

You can review the crontab with:

``` shell
make cron-show
```

