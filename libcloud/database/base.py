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

from libcloud.common.base import ConnectionUserAndKey, BaseDriver

__all__ = [
    "Database",
    "DatabaseDriver"
]


class Size(object):

    def __init__(self, id, name, extras=None):
        self.id = id
        self.name = name
        self.extras = extras or {}

    def __repr__(self):
        return ('<Size: id=%s, name=%s' % (self.id, self.description))


class Database(object):

    def __init__(self, id, name, engine, size, host, port, database, user, password, extras=None, driver=None):
        self.id = id
        self.name = name
        self.engine = engine
        self.size = size
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.extras = extras or {}
        self.driver = driver

    def destroy(self):
        self.driver.destroy_database(self.id)

    def __repr__(self):
        return ('<Database: id=%s, address=%s:%s>' % (self.id,
                                                    self.host, self.port))


class DatabaseDriver(BaseDriver):
    """
    Database driver.
    """
    connectionCls = ConnectionUserAndKey
    name = None
    website = None

    def list_engines(self):
        raise NotImplementedError

    def list_sizes(self):
        raise NotImplementedError

    def list_databases(self):
    	"""
        Return a list of databases.

        @rtype: C{list} of L{Database}
        """
    	raise NotImplementedError

    def get_database(self, database_id):
        raise NotImplementedError

    def create_database(self, name, size, engine):
    	raise NotImplementedError

    def destroy_database(self, database_id):
    	raise NotImplementedError
