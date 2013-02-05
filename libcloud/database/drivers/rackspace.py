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

from urllib import urlencode
from libcloud.common.base import ConnectionUserAndKey, JsonResponse
from libcloud.database.base import DatabaseDriver, Database


class RackspaceResponse(AWSGenericResponse):
    """
    Amazon RDS response class.
    """
    namespace = NS
    exceptions = {}
    xpath = 'Error'


class RackspaceConnection(SignedAWSConnection):
    version = VERSION
    host = HOST
    responseCls = RackspaceResponse


class RackspaceDatabaseDriver(Driver):
    name = 'Rackspace Cloud Database'
    website = 'http://www.rackspace.com/cloud/databases/techdetails/'
    connectionCls = RackspaceConnection

    # Look at ex_ methods for these:
    # http://developer.rackspace.com/cdb/api/v1.0/cdb-devguide/content/Database_Instances_Actions.html

    def list_sizes(self):
        """
        http://developer.rackspace.com/cdb/api/v1.0/cdb-devguide/content/GET_getFlavors__version___accountId__flavors_.html
        """

    def list_engines(self):
        return [
            'mysql',
        ]

    def list_databases(self):
        # http://developer.rackspace.com/cdb/api/v1.0/cdb-devguide/content/GET_getInstance__version___accountId__instances_.html

        params = {'Action': 'DescribeDBInstances'}
        data = self.connection.request(ROOT, params=params).object

    def get_database(self, database_id):
        # who knows

    def create_database(self, name, size, engine):
        # http://developer.rackspace.com/cdb/api/v1.0/cdb-devguide/content/POST_createInstance__version___accountId__instances_.html

    def destroy_database(self, database_id):
        # http://developer.rackspace.com/cdb/api/v1.0/cdb-devguide/content/DELETE_deleteInstance__version___accountId__instances__instanceId__.html

