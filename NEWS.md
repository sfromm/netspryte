NEWS
=====

## 17.06

* Change to different versioning scheme.
* Introduces database to track information about measurement instances.
* Introduces flask web frontend to view metrics and an API to query
  information about measurement instances from database.
* Support for deploying using *docker-compose* and containers.
* Updated Makefile to simplify deploying containers.
* Add janitor command for miscellaneous tasks such as cron job
  management, tagging, and so on.
* Add *rrd-merge-rrd* command to merge data from two RRD files into a
  single RRD.  Mostly useful when ifIndexes renumber or something
  similar.
* Remove deprecated static page generator.

## 0.1

* Basis for discovering and collecting information from devices.
  Focused on IF-MIB and CBQOS.
* Generates static pages and provides CGI to create graphs on the fly.

