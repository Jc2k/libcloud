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


class HerokuResponse(JsonResponse):
    pass


class HerokuConnection(ConnectionUserAndKey):
    """
    Connection class for the vCloud driver
    """

    responseCls = HerokuResponse
    host = 'postgres.heroku.com'
    token = None

    def request(self, *args, **kwargs):
        self._get_auth_token()
        return super(HerokuConnection, self).request(*args, **kwargs)

    def _get_auth_token(self):
        if self.token:
            return

        headers = {
            'Accept': 'application/json'
        }

        body = urlencode({
            'username': self.user_id,
            'password': self.key,
        })

        conn = self.conn_classes[self.secure](self.host, self.port)
        conn.request(method='POST', url='/login', body=body, headers=headers)

        resp = conn.getresponse()
        headers = dict(resp.getheaders())
        resp.read()

        try:
            self.token = headers['set-cookie']
        except KeyError:
            raise InvalidCredsError()

    def add_default_headers(self, headers):
        headers['Cookie'] = self.token
        headers['Accept'] = 'application/json'
        return headers


class HerokuDatabaseDriver(DatabaseDriver):

    name = 'Heroku Postgres'
    website = 'http://postgres.heroku.com/'
    connectionCls = HerokuConnection

    def list_engines(self):
        return ['postgres']
    
    def list_databases(self):
        res = self.connection.request('/api/dbs').object
        databases = []
        for db in res['dbs']:
            databases.append(self.get_database(db['id']))
        return databases

    def get_database(self, database_id):
        db = self.connection.request('/api/dbs/%s/info' % database_id).object
        conn = db['conn']

        d = Database(
            id = db['id'],
            name = db['name'],
            engine = 'postgres',
            host = conn['host'],
            port = conn['port'],
            database = conn['database'],
            user = conn['user'],
            password = conn['password'],
            )

        return db

    def create_database(self, name, size, engine):
        db = self.connection.request('/api/dbs/%s' % size.id, method='POST')
        print db

    def destroy_database(self, database_id):
        self.connection.request('/api/dbs/%s/destroy' % database.id, method='POST')


