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

import sys
import unittest

from libcloud.database.drivers.dummy import DummyDatabaseDriver
from libcloud.database.drivers.heroku import HerokuDatabaseDriver
from libcloud.test.database.mocks.heroku import HerokuMockHttp
from libcloud.test.secrets import DB_HEROKU_PARAMS

from .test_database import BaseDBTests


class RDSTests(BaseDBTests):

    def setUp(self):
        HerokuMockHttp.test = self
        HerokuDatabaseDriver.connectionCls.conn_classes = (None,
                                                      HerokuMockHttp)

        self.driver = HerokuDatabaseDriver(*DB_HEROKU_PARAMS)
        self.mock = DummyDatabaseDriver()

        self.setUpMock()


if __name__ == "__main__":
    sys.exit(unittest.main())
