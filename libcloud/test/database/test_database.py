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

from libcloud.database.base import Database, Size
from libcloud.database.drivers.dummy import DummyDatabaseDriver
from libcloud.database.types import DatabaseDoesNotExistError


class BaseDBTests(unittest.TestCase):
    def setUp(self):
        self.mock = self.driver = DummyDatabaseDriver()
        self.setUpMock()

    def setUpMock(self):
        self.testdb = self.mock.create_database(
            name='test_database',
            size=self.driver.list_sizes()[0],
            engine=self.driver.list_engines()[0],
        )

    def test_list_engines(self):
        protocols = self.driver.list_engines()
        self.assertTrue(isinstance(protocols, list))
        self.assertTrue(len(protocols) >= 1)

    def test_list_sizes(self):
        sizes = self.driver.list_sizes()
        self.assertTrue(isinstance(sizes, list))
        self.assertTrue(len(sizes) >= 1)
        for size in sizes:
            self.assertTrue(isinstance(size, Size))

    def test_list_databases(self):
        dbs = self.driver.list_databases()
        for db in dbs:
            self.assertTrue(isinstance(db, Database))

    def test_get_database(self):
        db = self.driver.list_databases()[0]
        got_db = self.driver.get_database(db.id)

        self.assertTrue(isinstance(got_db, Database))
        self.assertEqual(got_db.name, 'test_database')
        self.assertEqual(got_db.size.id, self.testdb.size.id)
        self.assertEqual(got_db.engine, self.testdb.engine)

    def test_destroy_database(self):
        db = self.driver.list_databases()[0]
        db.destroy()
        self.assertRaises(DatabaseDoesNotExistError, self.driver.get_database, db.id)

    def test_create_database(self):
        created = self.driver.create_database(name='test_database_2', size=self.driver.list_sizes()[0], engine=self.driver.list_engines()[0])
        self.assertTrue(isinstance(created, Database))

        db = self.driver.get_database(created.id)
        self.assertEqual(created.id, db.id)
        self.assertEqual(created.name, db.name)
        self.assertEqual(created.engine, db.engine)
        self.assertEqual(created.size.id, db.size.id)

        for db in self.driver.list_databases():
            if db.id == created.id:
                self.assertEqual(db.name, created.name)
                break
        else:
            self.fail("Newly created database didn't appear in list_databases")


if __name__ == "__main__":
    sys.exit(unittest.main())
