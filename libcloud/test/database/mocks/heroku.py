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
import json
import re

from libcloud.utils.py3 import httplib

from libcloud.test import MockHttpTestCase

from xml.etree import ElementTree as ET
from libcloud.utils.py3 import urlparse
from cgi import parse_qs

from libcloud.database.base import Size
from libcloud.database.types import DatabaseDoesNotExistError


class HerokuMockHttp(MockHttpTestCase):

    type = None

    routes = [
        ('^/api/dbs$', 'api_dbs'),
        ('^/api/dbs/(?P<PLAN>(dev|basic|zilla|mecha)+)$', 'api_dbs_PLAN'),
        ('^/api/dbs/(?P<DATABASEID>[^/]+)/info$', 'api_dbs_DATABASEID_info'),
        ('^/api/dbs/(?P<DATABASEID>[^/]+)/destroy$', 'api_dbs_DATABASEID_destroy'),
    ]

    def __init__(self, *args, **kwargs):
        MockHttpTestCase.__init__(self, *args, **kwargs)

    @property
    def driver(self):
        return self.test.mock

    def _get_method_name(self, type, use_param, qs, path):
        for route, method_name in self.routes:
            if re.match(route, path):
                return method_name
        return MockHttpTestCase._get_method_name(self, type, use_param, qs, path)

    def _get_database_id(self, url):
        return url.split('/')[3]

    def _from_database(self, db, verbose=False):
        info = {
            'id': db.id,
            'app_name': 'data-services-d3adb33f',
            'color': 'BLACK',
            'name': db.name,
            'created_at': '2013-01-09T20:07:00Z',
            'updated_at': '2013-01-09T20:07:00Z',
            'slug': db.name,
            'plan': db.size.id,
            'queries_count': 0,
            'resource_id': 'resource1@heroku.com',
            'encrypted_url': '010a2b2087949fc34e0a3b10d591c9472a5657df',
            'app_created_at': '2013-01-09T20:07:00Z',
            'db_created_at': '2013-01-09T20:07:00Z',
            'data_services': True,
            'recheck': True,
        }

        if verbose:
            info['conn'] = {
                'resource_name': 'thinking-wildly-1',
                'color_url': 'HEROKU_POSTGRESQL_GREEN',
                'color': 'GREEN',
                'port': db.port,
                'user': db.user,
                'pass': db.password,
                'database': db.database,
                'host': db.host,
            }
            info['collaborator'] = True
            info['promoter'] = True
            del info['recheck']

        return info

    def _login(self, method, url, body, headers):
        return (httplib.OK, body, {'set-cookie': 'password'}, httplib.responses[httplib.OK])

    def api_dbs(self, method, url, body, headers):
        assert method == 'GET'

        dbs = []
        for db in self.driver.list_databases():
            dbs.append(self._from_database(db))

        result = {
            'success': 'OK',
            'dbs': dbs,
        }

        body = json.dumps(result)
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def api_dbs_DATABASEID_info(self, method, url, body, headers):
        database_id = self._get_database_id(url)
        assert method == 'GET'

        db = self.driver.get_database(database_id)

        result = {
            'success': 'OK',
            'db': self._from_database(db, verbose=True),
        }

        body = json.dumps(result)
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def api_dbs_PLAN(self, method, url, body, headers):
        plan = url.split('/')[-1]
        assert method == 'POST'

        db = self.driver.create_database(
            name = 'heroku-dummy',
            engine = 'postgres',
            size = Size(id=plan, name=''),
        )

        result = {
        }

        body = json.dumps(result)
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def api_dbs_DATABASEID_destroy(self, method, url, body, headers):
        database_id = self._get_database_id(url)
        assert method == 'POST'

        db = self.driver.get_database(database_id)
        db.destroy()

        result = {
        }

        body = json.dumps(result)
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

