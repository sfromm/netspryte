SNMP Module Requirements
==============================

When implementing new modules that provide some way of accessing
SNMP information from a device, it must implement the following class
variables:

* **NAME** - Name of the class.  This should correlate to what is
  collected or the name of the MIB.
* **DATA** - A dictionary of name to OID.  This dictionary provides
  supplementary information about what the device exposes via SNMP.
* **STAT** - A dictionary of name to OID.  This dictionary provides the
  variables to collect telemetry information from the device.
* **XLATE** - A dictionary of key / value strings where the key contains
  substrings and the value what to replace the substring with.  Mostly
  used to clean up name before storing it in a database.
* **CONVERSION** - A dictionary of dictionaries.  Each sub-dictionary is
  provides a way to convert a SNMP returned value to a human-friendly
  string.  Examples include *ifAdminStatus* and *ifOperStatus*.
