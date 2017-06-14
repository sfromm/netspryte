netspryte
==========

*netspryte* is a library and set of utilities to query network equipment
and get structured data back that describes the device.

Prerequisites
----------------

You will need *docker* and *docker-compose* to install *netspryte*.
Please refer to documentation on installing these packages.

* [https://developer.fedoraproject.org/tools/docker/docker-installation.html](Getting started with Docker on Fedora)
* [https://wiki.debian.org/Docker](Docker on Debian)
* [https://docs.docker.com/engine/installation/](Install Docker)
* [https://docs.docker.com/compose/install/](Install Docker Compose)

For *docker-compose*, it should be enough to do a **pip install
docker-compose**.  See [https://docs.docker.com/compose/install/#alternative-install-options](Install using pip)
for details.

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

While the normal jobs will take care of initializing the database, you
can also do this directly:

``` shell
make initdb
```

This will start all the services.  To stop:

``` shell
make stop
```

At this time, you can jump down to the section on configuration and
start collecting data.

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

## Potential problems

The following are possible issues you might run into when deploying the
containers.

### SELinux enabled container host

If you plan to deploy this on a SELinux enabled system, you may have to
add the *:z* flag to the *$CONTAINER_DBDIR*, *$CONTAINER_CONFIGDIR*, and
*$CONTAINER_DATADIR* volume mounts in *docker-compose.yml*.  For example:

``` yaml
web:
  image: $WEB_IMAGE_NAME:$IMAGE_TAG
  container_name: $WEB_CONTAINER_NAME
  restart: $RESTART_POLICY
  ports:
    - "80:80"
  volumes:
    - $CONTAINER_CONFIGDIR:/etc/netspryte:z
    - $CONTAINER_DATADIR:/var/lib/netspryte/data:z

```

For more information, see:

* https://www.projectatomic.io/blog/2015/06/using-volumes-with-docker-can-cause-problems-with-selinux/

### Define dbhost in netspryte.cfg

The default database host is defined as **localhost**.  You will likely
want to update this to the *hostname* where the database container is
run.  This allows you to run the web and collector containers on
different hosts.

Configuration
----------------

Review *netspryte.cfg* for what is configurable.  The list of devices to
poll is defined by *devices* in the *general* section.

Once you have configured the list of devices to poll, it is time to
set up the collector to poll your devices.  This can be done with:

``` shell
make cron-add
```

You can review the crontab with:

``` shell
make cron-show
```

