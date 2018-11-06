

# Written by Stephen Fromm <stephenf nero net>
# Copyright (C) 2015-2017 University of Oregon
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
import netspryte.constants as C
from netspryte.system import SystemSession
from netspryte.utils import md5_string
from netspryte.utils.timer import Timer


class ExecSession(SystemSession):

    NAME = "exec"
    DESCRIPTION = "Execute command to collect data"

    def __init__(self, config):
        super(ExecSession, self).__init__(config)
        t = Timer("system exec run %s" % (self.host))
        t.start_timer()
        self.data = self.run_configured_commands()
        t.stop_timer()

    def run_command(self, cmd):
        args = C.get_config(self.config, cmd, 'command', None, None)
        fmt = C.get_config(self.config, cmd, 'format', None, 'json')
        t = Timer("system exec run %s: %s" % (self.host, args))
        t.start_timer()
        now1 = time.time()
        rc, out, err = self.run_process(args)
        data = self.parse_process_output(out, fmt)
        if data is None:
            return dict()
        if 'metrics' not in data:
            data['metrics'] = dict()
            for k in list(data.keys()):
                data['metrics'][k] = data.pop(k)
        if 'timestamp' not in data:
            data['timestamp'] = int(now1)
        if 'title' not in data:
            data['title'] = os.path.basename(args.split()[0])
        if 'presentation' not in data:
            data['presentation'] = args
        t.stop_timer()
        return data

    def run_configured_commands(self):
        data = dict()
        commands = list()
        if not C.config_has_section(self.config, 'system_exec'):
            return
        if C.config_has_option(self.config, 'system_exec', 'commands'):
            for cmd in C.get_config(self.config, 'system_exec', 'commands', None, [], islist=True):
                commands.append(cmd)
        if C.config_has_option(self.config, 'system_exec', 'command'):
            commands.append('system_exec')
        for cmd in sorted(commands):
            cmd_data = self.run_command(cmd)
            index = md5_string(cmd)
            data[index] = self.initialize_instance(ExecSession.NAME, index)
            data[index]['presentation'] = {'title': data['title'],
                                           'presentation': data['presentation']}
            data[index]['metrics'] = cmd_data['metrics']
            if 'attrs' in cmd_data:
                data[index]['attrs'] = cmd_data['attrs']
        return data
