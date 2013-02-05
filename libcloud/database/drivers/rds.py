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

from libcloud.utils.xml import findtext, findall
from libcloud.common.aws import AWSGenericResponse, SignedAWSConnection
from libcloud.database.base import DatabaseDriver, Database, Size

VERSION = '2013-01-10'
HOST = 'rds.amazonaws.com'
ROOT = '/'
NS = 'http://rds.amazonaws.com/doc/%s/' % (VERSION, )


class RDSConnection(AWSGenericResponse):
    """
    Amazon RDS response class.
    """
    namespace = NS
    exceptions = {}
    xpath = 'Error'


class RDSConnection(SignedAWSConnection):
    version = VERSION
    host = HOST
    responseCls = RDSConnection


class RDSDatabaseDriver(DatabaseDriver):
    name = 'RDS'
    website = 'http://aws.amazon.com/rds/'
    connectionCls = RDSConnection

    SIZES = {
        'db.t1.micro': Size(id='db.t1.micro', name=''),
        'db.m1.small': Size(id='db.m1.small', name=''),
        'db.m1.medium': Size(id='db.m1.medium', name=''),
        'db.m1.large': Size(id='db.m1.large', name=''),
        'db.m1.xlarge': Size(id='db.m1.xlarge', name=''),
        'db.m2.xlarge': Size(id='db.m2.xlarge', name=''),
        'db.m2.2xlarge': Size(id='db.m2.2xlarge', name=''),
        'db.m2.4xlarge': Size(id='db.m2.4xlarge', name=''),
    }

    def list_engines(self):
        return [
            'mysql'
            'oracle-se1',
            'oracle-se',
            'oracle-ee',
            'sqlserver-ee',
            'sqlserver-se',
            'sqlserver-ex',
            'sqlserver-web'
        ]

    def list_sizes(self):
        return self.SIZES.values()

    def list_databases(self):
        params = {'Action': 'DescribeDBInstances'}
        data = self.connection.request(ROOT, params=params).object

        xpath = 'DescribeDBInstancesResult/DBInstances/DBInstance'
        dbs = findall(element=data, xpath=xpath, namespace=NS)
        return [self._to_database(db) for db in dbs]

    def get_database(self, database_id):
        params = {
            'Action': 'DescribeDBInstances',
            'DBInstanceIdentifier': database_id,
        }
        data = self.connection.request(ROOT, params=params).object

        xpath = 'DescribeDBInstancesResult/DBInstances/DBInstance'
        db = findall(element=data, xpath=xpath, namespace=NS)[0]
        return self._to_database(db)

    def create_database(self, name, size, engine):
        params = {
            'Action': 'CreateDBInstance',
            'AllocatedStorage': str(5),
            'DBInstanceClass': size.id,
            'DBInstanceIdentifier': name,
            'Engine': engine,
            'MasterUser': 'admin',
            'MasterUserPassword': 'password',
        }
        data = self.connection.request(ROOT, params=params).object

        xpath = 'CreateDBInstanceResult/DBInstance'
        db = findall(element=data, xpath=xpath, namespace=NS)[0]
        return self._to_database(db)

    def destroy_database(self, database_id):
        #http://docs.aws.amazon.com/AmazonRDS/latest/APIReference/API_DeleteDBInstance.html
        params = {
            'Action': 'DeleteDBInstance',
            'DBInstanceIdentifier': database_id,
        }
        data = self.connection.request(ROOT, params=params).object

    def _to_database(self, el):
        name = findtext(element=el, xpath='DBInstanceIdentifier', namespace=NS)
        engine = findtext(element=el, xpath='Engine', namespace=NS)
        size = findtext(element=el, xpath='DBInstanceClass', namespace=NS)
        host = findtext(element=el, xpath='Endpoint/Address', namespace=NS)
        port = int(findtext(element=el, xpath='Endpoint/Port', namespace=NS))
        username = findtext(element=el, xpath='MasterUser', namespace=NS)

        db = Database(
            id = name,
            name = name,
            engine = engine,
            size = self.SIZES[size],
            host = host,
            port = port,
            database = 'example1',
            user = username,
            password = '',
            driver = self,
        )

        return db
