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

from libcloud.database.base import DatabaseDriver, Database, Size
from libcloud.database.types import DatabaseDoesNotExistError


class DummyDatabaseDriver(DatabaseDriver):

    name = 'Dummy'

    def __init__(self):
        self.databases = {}
        self.next_database_id = 0

    def list_engines(self):
        return ['sqlite']
    
    def list_sizes(self):
        return [Size(id='tiny', name='Tiny instance (512mb)')]

    def list_databases(self):
        return self.databases.values()

    def get_database(self, database_id):
        try:
            return self.databases[database_id]
        except KeyError:
            raise DatabaseDoesNotExistError(
                value='Database requested does not exist',
                driver=self,
                database_id=database_id
            )

    def create_database(self, name, size, engine):
        db = Database(
            id = str(self.next_database_id),
            name = name,
            engine = engine,
            size = size,
            host = 'localhost',
            port = 8080,
            database = 'database1',
            user = 'admin',
            password = 'password',
            driver = self,
        )
        self.next_database_id += 1
        self.databases[db.id] = db
        return db

    def destroy_database(self, database_id):
        try:
            del self.databases[database_id]
        except:
            raise DatabaseDoesNotExistError(
                value='Database requested does not exist',
                driver=self,
                database_id=database_id
            )
        return True
