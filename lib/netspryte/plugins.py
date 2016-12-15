# Written by Stephen Fromm <stephenf nero net>
# (C) 2016 University of Oregon
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

import imp
import glob
import os
import inspect
import logging
import sys
import warnings

from netspryte import constants as C
from netspryte.utils import *

class PluginLoader:
    '''
    Load modules/plugins from directories in python path.
    '''

    def __init__(self, module_paths):
        self.path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        self.module_paths = module_paths
        self.modules = dict()

    def _load_module(self, name, path):
        logging.debug("loading module %s from %s", name, path)
        cls = None
        if name in sys.modules:
            return sys.modules[name]
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            with open(path, 'r') as module_file:
                module = imp.load_source(name, path, module_file)
                logging.warn("loaded module %s", name)
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if obj.__module__ == os.path.splitext(module.__file__)[0]:
                cls = obj
        return (cls, module)

    def find(self, name, path):
        for root, dirs, files in os.walk(path):
            if name in files:
                return os.path.join(root, name)

    def get(self, name):
        ''' instantiate a plugin of the given name '''
        namext = "{0}.py".format(name)
        path = None
        for p in self.module_paths:
            if p.endswith('*'):
                p = p[0:-1]
            path = self.find(namext, os.path.join(self.path, p))
            if path:
                break
        if not path:
            logging.error("cannot find module %s", name)
            return self.modules
        name, ext = os.path.splitext(path)
        cls, module = self._load_module(name, path)
        self.modules[cls] = module
        return self.modules

    def all(self):
        ''' iterate over path and load plugins '''
        matches = list()
        for p in self.module_paths:
            matches.extend(glob.glob(os.path.join(self.path, p, "*.py")))

        for path in matches:
            name, ext = os.path.splitext(path)
            if path not in self.modules:
                cls, module = self._load_module(name, path)
                self.modules[cls] = module
        return self.modules

snmp_module_loader = PluginLoader(['snmp/host', 'snmp/vendor/*'])
