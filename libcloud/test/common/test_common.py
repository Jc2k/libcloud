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

import mock
import unittest

from libcloud.common.process import Connection, Response
from libcloud.common.base import BaseDriver


class MyDummyDriver(BaseDriver):
    connectionCls = Connection

    def dummy_operation(self):
        return self.connection.request('ls').body.split(',')


class TestSubprocessConnection(unittest.TestCase):

    @mock.patch('subprocess.Popen', autospec=True)
    def test_call_subprocess(self, popen):
        p = mock.Mock()
        p.communicate.return_value = ('a,b,c', '')
        p.returncode = 0
        popen.return_value = p

        m = MyDummyDriver(None)
        self.assertEqual(m.dummy_operation(), ['a', 'b', 'c'])

        popen.assert_called_with(['ls'], stdin=None, stdout=-1, stderr=-1)

