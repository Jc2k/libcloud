# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# This module provides a Connection like abstraction around subprocess
# interaction

import os
import shlex
import subprocess
from pipes import quote

from libcloud.common.types import *


class Response(object):

    def __init__(self, status, body, error):
        self.status = status
        self.body = body
        self.error = error

        if not self.success():
            raise self.parse_error()

        self.object = self.parse_body()

    def parse_body(self):
        return self.body

    def parse_error(self):
        raise ProviderError(self.body + " " + self.error, self.error)

    def success(self):
        return self.status == 0


class Connection(object):

    responseCls = Response
    log = None

    def  __init__(self, secure=True, host=None, port=None, url=None,
                  timeout=None):
        pass

    def connect(self):
        pass

    def get_command_prefix(self):
        return []

    def request(self, command, data='', capture_output=True):
        cmd = self.get_command_prefix()

        if not isinstance(command, list):
            cmd.extend(shlex.split(command))
        else:
            cmd.extend(command)

        if self.log:
            self.log.write(' '.join(quote(c) for c in cmd) + '\n')

        if not capture_output:
            stdout, stderr = '', ''
            returncode = self._silent_request(cmd, data)
        else:
            returncode, stdout, stderr = self._request(cmd, data)

        if self.log:
            self.log.write("# returncode is %d\n" % returncode)
            self.log.write("# -------- begin stdout ----------\n")
            self.log.write(stdout)
            self.log.write("# -------- begin stderr ----------\n")
            self.log.write(stderr)
            self.log.write("# -------- end ----------\n")

        return self.responseCls(returncode, stdout, stderr)

    def _request(self, command, data):
        stdin = subprocess.PIPE if data else None
        p = subprocess.Popen(command, stdin=stdin, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate(data)
        return p.returncode, stdout, stderr

    def _silent_request(self, command, data):
        # Popen.communicate hangs when child process creates forks and doesnt close the fd's
        # http://bugs.python.org/issue4216
        # http://bugs.python.org/issue13422
        stdin = subprocess.PIPE if data else None
        with open(os.devnull, "w") as null:
            p = subprocess.Popen(command, stdin=stdin, stdout=null, stderr=null)
            if data:
                p.stdin.write(data)
                p.stdin.close()
            return p.wait()


if __name__ == "__main__":
    p = Connection()
    r = p.request(["python", os.path.expanduser("~/daemon.py")])

