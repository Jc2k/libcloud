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

from libcloud.utils.py3 import httplib

from libcloud.test import MockHttpTestCase

from xml.etree import ElementTree as ET
from libcloud.utils.py3 import urlparse
from cgi import parse_qs
from libcloud.database.drivers.rds import NS
from libcloud.database.base import Size
from libcloud.database.types import DatabaseDoesNotExistError

class AWSParamAdaptor(object):

    """ FIXME: Hopefully by the time this branch is ready to land, my test-proposal branch will have landed. In which case this needs to go somewhere shared"""

    def __init__(self, container):
        self.container = container

    @classmethod
    def from_query_string(cls, query_string):
        return cls(parse_qs(query_string))

    @classmethod
    def from_url(cls, url):
        parsed = urlparse.urlparse(url)
        return cls.from_query_string(parsed.query)

    def get(self, key, default=None):
        val = self.container.get(key, [default])
        assert len(val) == 1
        return val[0]

    def __getitem__(self, key):
        val = self.container[key]
        assert len(val) == 1
        return val[0]

    def __contains__(self, key):
        return key in self.container

    def get_list_of_literals(self, key):
        """
        For AWS and similar, a list of literal values will be represented as follows:

            AvailabilityZones.member.1
            AvailabilityZones.member.2
        """
        params = self.container

        relevant_keys = [p for p in params.keys() if p.startswith(key)]
        relevant_keys.sort()

        if not len(relevant_keys):
            return []

        retval = []
        for key in relevant_keys:
            tup = key.split(".")
            assert len(tup) == 3
            val = params[key]
            assert len(val) == 1
            retval.append(val[0])

        return retval

    def get_list_of_structs(self, key):
        """
        For AWS and similar a list of structs will be represented as follows:

            Listeners.members.1.InstancePort
            Listeners.members.1.LoadBalancerPort
            Listeners.members.2.InstancePort
            Listeners.members.2.LoadBalancerPort

        It can also handle:

            realiplist.0.ip
            realiplist.1.ip
        """
        params = self.container

        relevant_keys = [p for p in params.keys() if p.startswith(key)]
        relevant_keys.sort()

        if not len(relevant_keys):
            return []

        retval = []
        idx = -1
        for key in relevant_keys:
            tup = key.split(".")
            assert len(tup) in (3,4)
            if idx != int(tup[-2]):
                s = {}
                retval.append(s)
                idx = int(tup[-2])
            val = params[key]
            assert len(val) == 1
            s[tup[-1]] = val[0]

        return retval


class RDSMockHttp(MockHttpTestCase):

    type = None
    use_param = 'Action'

    def __init__(self, *args, **kwargs):
        MockHttpTestCase.__init__(self, *args, **kwargs)

    @property
    def driver(self):
        return self.test.mock

    def _verify_signature(self, params):
        self.assertIn("Timestamp", params)
        self.assertEqual(params["SignatureVersion"], "2")
        self.assertEqual(params["SignatureMethod"], "HmacSHA256")
        self.assertIn("Signature", params)
        self.assertIn("Version", params)

    def _from_database(self, db):
        inst = ET.Element('DBInstance')
            
        ET.SubElement(inst, 'DBInstanceIdentifier').text = db.name
        ET.SubElement(inst, 'Engine').text = db.engine
        ET.SubElement(inst, 'DBInstanceClass').text = db.size.id

        epoint = ET.SubElement(inst, 'Endpoint')
        ET.SubElement(epoint, 'Port').text = str(db.port)
        ET.SubElement(epoint, 'Address').text = db.host

        ET.SubElement(epoint, 'MasterUsername').text = db.user
        return inst

    def _get_database_by_name(self, name):
        for db in self.driver.list_databases():
            if db.name == name:
                return db
        else:
            raise DatabaseDoesNotExistError

    def _DescribeDBInstances(self, method, url, body, headers):
        params = AWSParamAdaptor.from_url(url)
        self._verify_signature(params)

        resp = ET.Element('DescribeDBInstancesResponse', {'xmlns': NS})
        result = ET.SubElement(resp, 'DescribeDBInstancesResult')
        instances = ET.SubElement(result, 'DBInstances')

        if 'DBInstanceIdentifier' in params:
            dbs = [d for d in self.driver.list_databases() if d.name == params['DBInstanceIdentifier']]
            if len(dbs) == 0:
                raise DatabaseDoesNotExistError(value='', driver=self, database_id=params['DBInstanceIdentifier'])
            instances.append(self._from_database(dbs[0]))
        else:
          for db in self.driver.list_databases():
                instances.append(self._from_database(db))

        body = ET.tostring(resp)
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _CreateDBInstance(self, method, url, body, headers):
        params = AWSParamAdaptor.from_url(url)
        self._verify_signature(params)

        db = self.driver.create_database(
            name=params['DBInstanceIdentifier'],
            engine = params['Engine'],
            size=Size(id=params['DBInstanceClass'], name=''),
        )

        resp = ET.Element('CreateDBInstanceResponse', {'xmlns': NS})
        result = ET.SubElement(resp, 'CreateDBInstanceResult')
        result.append(self._from_database(db))
        body = ET.tostring(resp)
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _DeleteDBInstance(self, method, url, body, headers):
        params = AWSParamAdaptor.from_url(url)
        self._verify_signature(params)

        db = self._get_database_by_name(params['DBInstanceIdentifier'])
        self.driver.destroy_database(db.id)

        response = ET.Element('DeleteDBInstanceResponse', {'xmlns': NS})
        result = ET.SubElement(response, 'DeleteDBInstanceResult')
        result.append(self._from_database(db))

        body = ET.tostring(result)
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])


if __name__ == "__main__":
    sys.exit(unittest.main())
