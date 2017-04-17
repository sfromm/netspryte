# Written by Stephen Fromm <stephenf nero net>
# Copyright (C) 2016-2017 University of Oregon
#
# This file is part of netspryte
#
# netspryte is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# netspryte is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with netspryte.  If not, see <http://www.gnu.org/licenses/>.

import time
import logging

class Timer(object):

    '''
    A class to help measure how long a section of code takes to run.

    '''
    def __init__(self, name=None):
        self._start = time.time()
        self._stop = 0
        self._elapsed = 0
        self._name = "Generic Timer"
        if name:
            self.name = name

    def start_timer(self):
        self.start = time.time()

    def stop_timer(self):
        self.stop = time.time()
        self.elapsed = self.stop - self.start
        logging.warn("%s elapsed time: %.3fs", self.name, self.elapsed)

    '''
    The following methods allow one to invoke Timer() thusly:

    with Timer() as t:
        run_method()
    '''
    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, *args):
        self.stop = time.time()
        self.elapsed = self.stop - self.start
        logging.warn("%s elapsed time: %.3fs", self.name, self.elapsed)

    @property
    def start(self):
        return self._start

    @start.setter
    def start(self, arg):
        self._start = arg

    @property
    def stop(self):
        return self._stop

    @stop.setter
    def stop(self, arg):
        self._stop = arg

    @property
    def elapsed(self):
        return self._elapsed

    @elapsed.setter
    def elapsed(self, arg):
        self._elapsed = arg

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, arg):
        self._name = arg
