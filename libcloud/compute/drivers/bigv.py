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

"""
BigV (http://bigv.io) driver.
"""

import base64
import binascii
import os

try:
    import simplejson as json
except:
    import json

from libcloud.utils.py3 import httplib
from libcloud.utils.py3 import b

from libcloud.common.types import LibcloudError
from libcloud.compute.providers import Provider
from libcloud.common.base import JsonResponse, ConnectionUserAndKey
from libcloud.compute.base import is_private_subnet
from libcloud.compute.types import NodeState, InvalidCredsError
from libcloud.compute.base import Node, NodeDriver, NodeImage, NodeSize


LOCATIONS = ['uk0', ]
DEFAULT_LOCATION = LOCATIONS[0]


class BigVResponse(JsonResponse):

    valid_response_codes = [httplib.OK, httplib.ACCEPTED, httplib.CREATED,
                            httplib.NO_CONTENT]

    def parse_error(self):
        if self.status == 401:
            raise InvalidCredsError('Invalid credentials')
        return self.body

    def success(self):
        return self.status in self.valid_response_codes


class BigVConnection(ConnectionUserAndKey):

    responseCls = BigVResponse

    def add_default_headers(self, headers):
        user_b64 = base64.b64encode(b('%s:%s' % (self.user_id, self.key)))
        headers['Authorization'] = 'Basic %s' % (user_b64.decode('utf-8'))
        return headers


class BigVNodeDriver(NodeDriver):

    type = Provider.BIGV
    name = 'BigV'
    website = 'http://bigv.io'
    connectionCls = BigVConnection
    features = {'create_node': ['generates_password']}

    def __init__(self, *args, **kwargs):
        """
        @inherits: L{NodeDriver.__init__}

        @keyword    location: Location which should be used
        @type       location: C{str}
        """

        if 'location' in kwargs:
            if kwargs['location'] not in LOCATIONS:
                msg = 'Invalid location: "%s". Valid locations: %s'
                raise LibcloudError(msg % (kwargs['location'],
                                    ', '.join(LOCATIONS)), driver=self)
        else:
            kwargs['location'] = DEFAULT_LOCATION

        super(BigVNodeDriver, self).__init__(*args, **kwargs)

        if 'group' in kwargs:
            self.group = kwags['group']
        else:
            self.group = 'default'

        self.account = kwargs['account']

        self.group_url = '/accounts/%s/groups/%s' % (self.account, self.group)

        self.connection.host = kwargs['location'] + '.bigv.io'

    def list_images(self):
	images = ['centos-5.8', 'centos-6.3', 'oneiric', 'precise', 'squeeze',
                  'symbiosis', 'wheezy', 'winweb2k8r2', 'winstd2012', 'none', ]
        retval = []
        for image in images:
            retval.append(NodeImage(id=image, name=image, driver=self.connection.driver, extra={}))
        return retval

    def list_sizes(self):
        return []

        for value in result:
            size = NodeSize(id=value['name'], name=value['name'],
                            ram=value['memory'], disk=value['disk'],
                            bandwidth=None, price=0.0,
                            driver=self.connection.driver)
            sizes.append(size)

        return sizes

    def list_nodes(self):
        result = self.connection.request(self.group_url+'?view=overview').object

        nodes = []
        for value in result.get('virtual_machines', []):
            node = self._to_node(value)
            nodes.append(node)

        return nodes

    def reboot_node(self, node):
        data = json.dumps({'power_on': False})
        result = self.connection.request(self.group_url+'/virtual_machines/%s' % (node.id),
                                         data=data, method='PUT')

        data = json.dumps({'power_on': True})
        result = self.connection.request(self.group_url+'/virtual_machines/%s' % (node.id),
                                         data=data, method='PUT')

    def destroy_node(self, node):
        result = self.connection.request(self.group_url+'/virtual_machines/%s' % (node.id),
                                         method='DELETE')
        return result.status == httplib.NO_CONTENT

    def create_node(self, **kwargs):
        name = kwargs['name']
        size = kwargs['size']
        image = kwargs['image']

        generated_password = binascii.hexlify(os.urandom(8))
        generated_password = "ZBDcyliNgD"

        payload = {
            "reimage": {
                "distribution": image.id,
                "root_password": generated_password,
                "type": "application/vnd.bigv.reimage",
            },
            "discs": [{
                "storage_grade": "sata",
                "size": 5120,
                "label": "vda",
                "type": "application/vnd.bigv.disc",
            }],
            "virtual_machine": {
                "power_on": True,
                "hardware_profile": None,
                "autoreboot_on": True,
                "cdrom_url": None,
                "memory": 1024,
                "name": name,
                "cores": "1",
                "type": "application/vnd.bigv.virtual-machine",
            },
            "type": "application/vnd.bigv.vm-create",
        }

        data = json.dumps(payload)
        result = self.connection.request(self.group_url+'/vm_create', data=data,
                                         method='POST')
        return self._to_node(result.object['virtual_machine'], generated_password=generated_password)

    def _iter_interfaces(name):
        # Structure contains: label, vlan_num, mac, list of ips (including ipv6), extra_ips
        result = self.connection.request(self.group_url+'/virtual_machines/%s/nics' % (node.id))
        for row in result:
            yield row['ips'][0]

    def _to_node(self, data, generated_password=None):
        public_ips = []
        private_ips = []

        for ip in self._iter_interfaces(data['name']):
            if is_private_subnet(ip):
                private_ips.append(ip)
            else:
                public_ips.append(ip)

        extra = {
            'management_address': data['management_address'],
            'cores': data['cores'],
            'memory': data['memory'],
            'hostname': data['hostname'],
        }

        if data['deleted'] == False:
            state = NodeState.TERMINATED
        elif data['power_on'] == False:
            state = NodeState.PENDING
        else:
            state = NodeState.RUNNING

        if generated_password:
            extra['password'] = generated_password

        node = Node(id=data['id'], name=data['name'], state=state,
                    public_ips=public_ips, private_ips=private_ips,
                    driver=self.connection.driver, extra=extra)

        return node
