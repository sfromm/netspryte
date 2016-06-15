# Written by Stephen Fromm <stephenf nero net>
# (C) 2015-2016 University of Oregon
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.

import snmpryte
import sys
import logging
import argparse

from snmpryte import constants as C
from snmpryte.utils import *

class BaseCommand(object):

    def __init__(self, daemonize=False):
        self.usage = 'usage: %prog [options]'
        self.daemonize = daemonize
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('-v', '--verbose',
                                 action="count", default=C.DEFAULT_VERBOSE,
                                 help="Be verbose. Use more than once to increase verbosity.")
        self.parser.add_argument('--datadir', default=C.DEFAULT_DATADIR,
                                 help='Path to data directory')
        self.parser.add_argument('--nofork', default=False, action='store_true',
                                 help='Do not fork; useful for debugging')

    def daemonize(self):
        pass

    def execute(self):
        if self.daemonize:
            return self._daemonize()
        else:
            try:
                return self.run()
            except KeyboardInterrupt:
                print()
