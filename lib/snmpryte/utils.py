# Written by Stephen Fromm <stephenf nero net>
# (C) 2016 University of Oregon
#
# This file is part of snmpryte
#
# snmpryte is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# snmpryte is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with snmpryte.  If not, see <http://www.gnu.org/licenses/>.

import logging
from snmpryte import constants as C

def setup_logging(program='snmpryte'):
    ''' set up logging '''
    C.DEFAULT_LOG_LEVEL = int(C.DEFAULT_LOG_LEVEL)
    if C.DEFAULT_LOG_LEVEL >= 2:
        loglevel = 'DEBUG'
    elif C.DEFAULT_LOG_LEVEL >= 1:
        loglevel = 'INFO'
    else:
        loglevel = 'WARN'

    if C.DEFAULT_VERBOSE and loglevel == 'WARN':
        loglevel = 'INFO'

    numlevel = getattr(logging, loglevel.upper(), None)
    if not isinstance(numlevel, int):
        raise ValueError('Invalid log level: %s' % loglevel)

    logargs = {}
    logargs['level'] = numlevel
    logargs['datefmt'] = '%FT%T'
    logargs['format'] = C.DEFAULT_LOG_FORMAT
    logging.basicConfig(**logargs)
