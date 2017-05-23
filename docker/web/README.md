Web Front-end Container
=============================

Building container
----------------------

To build the container, use the Makefile from the top-level directory of
the repository:

``` shell
make docker-web
```

Running container
---------------------

``` shell
docker run -d -p 80:80 -v netspryte:/etc/netspryte -v 
```
