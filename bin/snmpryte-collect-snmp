#!/usr/bin/python
__requires__ = ['snmpryte']
try:
    import pkg_resources
except Exception:
    pass
import sys

from snmpryte.commands.collectsnmp import CollectSnmpCommand

if __name__ == '__main__':
    cmd = CollectSnmpCommand()
    sys.exit(cmd.execute())
