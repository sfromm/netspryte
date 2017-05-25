TODO
=====

Goals for 17.06
-------------------

* DONE Change to different versioning scheme: YY.MM
* DONE Continue build support for influxdb write support
* DONE Move away from json files; use database to store information
* DONE Move to flask web interface
* DONE Move to plugin approach for running snmp modules
* TODO Ability to define RRD DEFs in database - needed to override
  individual graphs.

Goals for 0.1
----------------

* DONE cbqos and interface classes have complete set of meta keys: id, class,
  idx, title, and description
* DONE Finish separation of datadir and wwwdir
* DONE Have a working template:
  * DONE sidebar with links to relevant anchors
  * DONE create detail pages: present historical data
* DONE create rpm
* DONE ability to read a site local json that updates the json cached by this
  application.
* DONE influxdb database backend write support
* DONE CGI to produce PNG graphs
* DONE add date/time stamp to graph
