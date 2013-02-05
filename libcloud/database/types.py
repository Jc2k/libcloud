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

from libcloud.common.types import LibcloudError

__all__ = [
    'Provider',
    'DatabaseError',
    'DatabaseDoesNotExistError',
    'DatabaseAlreadyExistsError',
]


class Provider(object):
    DUMMY = 'dummy'
    HEROKU = 'heroku'
    RDS = 'rds'
    RACKSPACE = 'rackspace'


class DatabaseError(LibcloudError):
    error_type = 'DatabaseError'
    kwargs = ('database_id', )

    def __init__(self, value, driver, database_id):
        self.database_id = database_id
        super(DatabaseError, self).__init__(value=value, driver=driver)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return ('<%s in %s, zone_id=%s, value=%s>' %
                (self.error_type, repr(self.driver),
                 self.zone_id, self.value))


class DatabaseDoesNotExistError(DatabaseError):
    error_type = 'DatabaseDoesNotExistError'


class DatabaseAlreadyExistsError(DatabaseError):
    error_type = 'DatabaseAlreadyExistsError'

