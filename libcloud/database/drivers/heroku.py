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
import json

from libcloud.common.base import ConnectionUserAndKey, JsonResponse
from libcloud.common.types import InvalidCredsError
from libcloud.database.base import DatabaseDriver, Database, Size


class HerokuResponse(JsonResponse):
    pass


class HerokuConnection(ConnectionUserAndKey):
    """
    Connection class for the vCloud driver
    """

    responseCls = HerokuResponse
    host = 'postgres.heroku.com'
    token = None

    def _get_auth_token(self):
        if self.token:
            return self.token

        # Prior to Feb 4th 2013 one could POST to postgres.heroku.com/login and retrive
        # the Set-Cookie header and give that to future requests
        # From Feb 5th onwards all logins now go via api.heroku.com and now use a
        # seemingly undocumented oauth scheme :(

        raise InvalidCredsError(driver=self.driver)

        headers = {
            'Accept': 'application/json'
        }

        body = urlencode({
            'username': self.user_id,
            'password': self.key,
        })

        conn = self.conn_classes[self.secure]('api.heroku.com', self.port)
        conn.request(method='POST', url='/login', body=body, headers=headers)
        resp = conn.getresponse()

        self.token = json.loads(resp.read())['api_key']
        return self.token

    def add_default_headers(self, headers):
        # headers['Authorization'] = 'OAuth ' + self._get_auth_token()
        headers['Cookie'] = self.COOKIE
        headers['Accept'] = 'application/json'
        return headers


class HerokuDatabaseDriver(DatabaseDriver):

    name = 'Heroku Postgres'
    website = 'http://postgres.heroku.com/'
    connectionCls = HerokuConnection

    SIZES = {
        'dev': Size(id='dev', name='Dev Plan (free)'),
        'basic': Size(id='basic', name='Basic Plan'),
        'crane': Size(id='crane', name='Crane'),
        'kappa': Size(id='kappa', name='Kappa'),
        'ronin': Size(id='ronin', name='Ronin'),
        'fugu': Size(id='fugu', name='Fugu'),
        'ika': Size(id='ika', name='Ika'),
        'zilla': Size(id='zilla', name='Zilla'),
        'baku': Size(id='baku', name='Baku'),
        'mecha': Size(id='mecha', name='Mecha'),
    }

    def list_engines(self):
        return ['postgres']

    def list_sizes(self):
        return self.SIZES.values()
    
    def list_databases(self):
        res = self.connection.request('/api/dbs').object
        databases = []
        for db in res['dbs']:
            databases.append(self.get_database(db['id']))
        return databases

    def get_database(self, database_id):
        res = self.connection.request('/api/dbs/%s/info' % database_id).object

        info = res['db']
        conn = info['conn']

        db = Database(
            id = info['id'],
            name = info['name'],
            engine = 'postgres',
            size = self.SIZES[info['plan']],
            host = conn['host'],
            port = conn['port'],
            database = conn['database'],
            user = conn['user'],
            password = conn['pass'],
            driver = self,
            )

        return db

    def create_database(self, name, size, engine):
        db = self.connection.request('/api/dbs/%s' % size.id, method='POST')
        print db

    def destroy_database(self, database_id):
        self.connection.request('/api/dbs/%s/destroy' % database_id, method='POST')

    def list_backups(self, database_id):
        self.connection.request('/api/dbs/%s/backups' % database_id)

    def create_backup(self, database_id):
        self.connection.request('/api/dbs/%s/backup' % database_id, method='POST')
        # {"success":"OK","db":{"id":91769,"app_name":"data-services-1b0699f5","color":"GREEN","name":"dry-stream-40","created_at":"2012-12-14T17:16:00Z","updated_at":"2012-12-14T17:16:10Z","slug":"dry-stream-40","plan":"dev","queries_count":0,"user_id":2936,"resource_id":"resource1607206@heroku.com","encrypted_url":"O6U1HrbxsyQuIY+7ItLed2Q3cXkcqvRibtJAvV1EiByls7siZLhH3Z30e2ArWxoknTDn+V1z8oBMYcuncNmUm6U4pWwt+QZtsweSiDm2IzcM+AH0myeWPTftoMg6kEBEok/iSdiLQXP+Yq9QPIPm++LPcmoMbSRL+Ir/0IL7IgQ=--h5JN/gksRA5JaZE4Y2iX+g==","config_vars":{"PGBACKUPS_URL":"https://352020:1wxcepllftdgwc8xtdvqnm4bd@pgbackups.herokuapp.com/client","DATABASE_URL":"postgres://hievfyvexcldct:yDaDoSdZZ_58EjHEWWyF9H6y5V@ec2-54-243-178-223.compute-1.amazonaws.com:5432/dhtvgtlef75e9","HEROKU_POSTGRESQL_GREEN_URL":"postgres://hievfyvexcldct:yDaDoSdZZ_58EjHEWWyF9H6y5V@ec2-54-243-178-223.compute-1.amazonaws.com:5432/dhtvgtlef75e9"},"pg_dbs":{"postgres://hievfyvexcldct:yDaDoSdZZ_58EjHEWWyF9H6y5V@ec2-54-243-178-223.compute-1.amazonaws.com:5432/dhtvgtlef75e9":{"color_url":"HEROKU_POSTGRESQL_GREEN","color":"GREEN","url":"postgres://hievfyvexcldct:yDaDoSdZZ_58EjHEWWyF9H6y5V@ec2-54-243-178-223.compute-1.amazonaws.com:5432/dhtvgtlef75e9","sha":"583ceabdf383c1dd0fd35d89d1999d959ebfc4fe66f9bc3dc3c486ce595b6a10","connect":"psql -h ec2-54-243-178-223.compute-1.amazonaws.com -U hievfyvexcldct -d dhtvgtlef75e9 -W ","host":"ec2-54-243-178-223.compute-1.amazonaws.com","database":"dhtvgtlef75e9","user":"hievfyvexcldct","pass":"yDaDoSdZZ_58EjHEWWyF9H6y5V","port":"5432"}},"pg_db":{"color_url":"HEROKU_POSTGRESQL_GREEN","color":"GREEN","url":"postgres://hievfyvexcldct:yDaDoSdZZ_58EjHEWWyF9H6y5V@ec2-54-243-178-223.compute-1.amazonaws.com:5432/dhtvgtlef75e9","sha":"583ceabdf383c1dd0fd35d89d1999d959ebfc4fe66f9bc3dc3c486ce595b6a10","connect":"psql -h ec2-54-243-178-223.compute-1.amazonaws.com -U hievfyvexcldct -d dhtvgtlef75e9 -W ","host":"ec2-54-243-178-223.compute-1.amazonaws.com","database":"dhtvgtlef75e9","user":"hievfyvexcldct","pass":"yDaDoSdZZ_58EjHEWWyF9H6y5V","port":"5432"},"conn":{"port":"5432","color_url":"HEROKU_POSTGRESQL_GREEN","color":"GREEN","url":"postgres://hievfyvexcldct:yDaDoSdZZ_58EjHEWWyF9H6y5V@ec2-54-243-178-223.compute-1.amazonaws.com:5432/dhtvgtlef75e9","sha":"583ceabdf383c1dd0fd35d89d1999d959ebfc4fe66f9bc3dc3c486ce595b6a10","connect":"psql -h ec2-54-243-178-223.compute-1.amazonaws.com -U hievfyvexcldct -d dhtvgtlef75e9 -W ","host":"ec2-54-243-178-223.compute-1.amazonaws.com","database":"dhtvgtlef75e9","user":"hievfyvexcldct","pass":"yDaDoSdZZ_58EjHEWWyF9H6y5V"},"app_created_at":"2012-12-14T17:16:00Z","db_created_at":"2012-12-14T17:16:00Z","data_services":true},"backup":{"id":5739288,"user_id":352020,"from_url":"postgres://hievfyvexcldct:yDaDoSdZZ_58EjHEWWyF9H6y5V@ec2-54-243-178-223.compute-1.amazonaws.com:5432/dhtvgtlef75e9","from_name":"dhtvgtlef75e9","to_url":"s3://hkpgbackups/app10062080@heroku.com/b001.dump","to_name":"BACKUP","created_at":"February 05, 2013 11:57","started_at":null,"updated_at":null,"finished_at":null,"error_at":null,"destroyed_at":null,"progress":null,"size":"capturing...","expire":null,"cleaned_at":null,"name":"b001"}}
        self.connection.request('/api/dbs/%s/backup/b001' % database_id)
        #{"success":"OK","backup":{"id":5739288,"user_id":352020,"from_url":"postgres://hievfyvexcldct:yDaDoSdZZ_58EjHEWWyF9H6y5V@ec2-54-243-178-223.compute-1.amazonaws.com:5432/dhtvgtlef75e9","from_name":"dhtvgtlef75e9","to_url":"s3://hkpgbackups/app10062080@heroku.com/b001.dump","to_name":"BACKUP","created_at":"February 05, 2013 11:57","started_at":"2013/02/05 11:57.32","updated_at":"2013-02-05 11:57:33 +0000","finished_at":"2013/02/05 11:57.33","error_at":null,"destroyed_at":null,"progress":"upload done","size":"1.4KB","expire":null,"cleaned_at":null,"user":"app10062080@heroku.com","type":"backup","duration":1.965438,"log":"Started:  Tue Feb 5 11:57:32 UTC 2013\nLocation: a8f38d0f-9880-44fd-bdd5-86a5e330bcbe:/tmp/Jz6zxYK5YN\n+ locate_binaries\n+ '[' -n bin/ ']'\n++ tail -1\n++ ls bin//psql-8.3.21-64bit bin//psql-8.4.14-64bit bin//psql-9.0.10-64bit bin//psql-9.1.6-64bit bin//psql-9.2.1-64bit\n+ psql=bin//psql-9.2.1-64bit\n++ tail -1\n++ ls bin//pv-1.1.4-64bit\n+ pv=bin//pv-1.1.4-64bit\n+ psql=bin//psql-9.2.1-64bit\n+ echo 'psql: bin//psql-9.2.1-64bit'\npsql: bin//psql-9.2.1-64bit\n+ pv=bin//pv-1.1.4-64bit\n+ echo 'pv: bin//pv-1.1.4-64bit'\npv: bin//pv-1.1.4-64bit\n+ [[ s3 = \\\\p\\\\o\\\\s\\\\t\\\\g\\\\r\\\\e\\\\s ]]\n+ [[ postgres = \\\\p\\\\o\\\\s\\\\t\\\\g\\\\r\\\\e\\\\s ]]\n+++ from_version\n++++ PGPASSWORD=yDaDoSdZZ_58EjHEWWyF9H6y5V\n++++ bin//psql-9.2.1-64bit '-p 5432' -h ec2-54-243-178-223.compute-1.amazonaws.com -Uhievfyvexcldct -d dhtvgtlef75e9 -t -A -c 'SELECT VERSION()'\n++++ awk '{print $2}'\n+++ version=9.1.6\n+++ echo 9.1.6\n++ versioned_binary pg_dump 9.1.6\n++ binary=pg_dump\n++ version=9.1.6\n+++ sed -r 's/\\\\.[0-9]+$//'\n+++ echo 9.1.6\n++ major_v=9.1\n++ '[' 9.1 -lt 9 ']'\nbin/brie: line 145: [: 9.1: integer expression expected\n++ binpath=bin/\n+++ tail -1\n+++ ls bin//pg_dump-9.1.6-64bit\n++ maybe=bin//pg_dump-9.1.6-64bit\n++ echo bin//pg_dump-9.1.6-64bit\n+ pg_dump=bin//pg_dump-9.1.6-64bit\n+ echo 'pg_dump: bin//pg_dump-9.1.6-64bit'\npg_dump: bin//pg_dump-9.1.6-64bit\n+ backup\n++ basename s3://hkpgbackups/app10062080@heroku.com/b001.dump\n+ dump_file=/tmp/Jz6zxYK5YN/b001.dump\n++ dirname s3://hkpgbackups/app10062080@heroku.com/b001.dump\n+ bucket=s3://hkpgbackups/app10062080@heroku.com/\n+ from_summary\n++ dirname bin/brie\n+ run_on_from bin/brie_summary.sql\n+ PGPASSWORD=yDaDoSdZZ_58EjHEWWyF9H6y5V\n+ bin//psql-9.2.1-64bit '-p 5432' -h ec2-54-243-178-223.compute-1.amazonaws.com -Uhievfyvexcldct -f bin/brie_summary.sql dhtvgtlef75e9\n Schema | Name | Type | Info \n--------+------+------+------\n(0 rows)\n\n+ echo dump_progress: start\ndump_progress: start\n+ bin//pv-1.1.4-64bit --name dump_progress --bytes --force\n+ PGPASSWORD=yDaDoSdZZ_58EjHEWWyF9H6y5V\n+ bin//pg_dump-9.1.6-64bit --verbose '-p 5432' -h ec2-54-243-178-223.compute-1.amazonaws.com -Uhievfyvexcldct -Fc --no-acl --no-owner dhtvgtlef75e9\npg_dump-9.1.6-64bit: reading schemas\npg_dump-9.1.6-64bit: reading user-defined tables\npg_dump-9.1.6-64bit: reading extensions\npg_dump-9.1.6-64bit: reading user-defined functions\npg_dump-9.1.6-64bit: reading user-defined types\npg_dump-9.1.6-64bit: reading procedural languages\npg_dump-9.1.6-64bit: reading user-defined aggregate functions\npg_dump-9.1.6-64bit: reading user-defined operators\npg_dump-9.1.6-64bit: reading user-defined operator classes\npg_dump-9.1.6-64bit: reading user-defined operator families\npg_dump-9.1.6-64bit: reading user-defined text search parsers\npg_dump-9.1.6-64bit: reading user-defined text search templates\npg_dump-9.1.6-64bit: reading user-defined text search dictionaries\npg_dump-9.1.6-64bit: reading user-defined text search configurations\npg_dump-9.1.6-64bit: reading user-defined foreign-data wrappers\npg_dump-9.1.6-64bit: reading user-defined foreign servers\npg_dump-9.1.6-64bit: reading default privileges\npg_dump-9.1.6-64bit: reading user-defined collations\npg_dump-9.1.6-64bit: reading user-defined conversions\npg_dump-9.1.6-64bit: reading type casts\npg_dump-9.1.6-64bit: reading table inheritance information\npg_dump-9.1.6-64bit: reading rewrite rules\npg_dump-9.1.6-64bit: finding extension members\npg_dump-9.1.6-64bit: finding inheritance relationships\npg_dump-9.1.6-64bit: reading column info for interesting tables\npg_dump-9.1.6-64bit: flagging inherited columns in subtables\npg_dump-9.1.6-64bit: reading indexes\npg_dump-9.1.6-64bit: reading constraints\npg_dump-9.1.6-64bit: reading triggers\npg_dump-9.1.6-64bit: reading large objects\npg_dump-9.1.6-64bit: reading dependency data\npg_dump-9.1.6-64bit: saving encoding = UTF8\npg_dump-9.1.6-64bit: saving standard_conforming_strings = off\npg_dump-9.1.6-64bit: saving database definition\ndump_progress: 1.38kB \n\n+ split -b 5000000000 /tmp/Jz6zxYK5YN/b001.dump /tmp/Jz6zxYK5YN/b001.dump.\n+ dump_files=/tmp/Jz6zxYK5YN/b001.dump\n+ '[' -e /tmp/Jz6zxYK5YN/b001.dump.ab ']'\n++ bin/filesize /tmp/Jz6zxYK5YN/b001.dump\n+ echo dump_progress: 1.4KB\ndump_progress: 1.4KB\n+ echo dump_progress: done\ndump_progress: done\n+ echo upload_progress: start\nupload_progress: start\n+ bin/s3cmd --progress put /tmp/Jz6zxYK5YN/b001.dump s3://hkpgbackups/app10062080@heroku.com/\n/tmp/Jz6zxYK5YN/b001.dump -> s3://hkpgbackups/app10062080@heroku.com/b001.dump  [1 of 1]\n\nupload_progress:  1411.0 of  1411.0   100% in    0s   253.30 kBB/s\nupload_progress:  1411.0 of  1411.0   100% in    0s    19.81 kBB/s  done\n++ bin/filesize /tmp/Jz6zxYK5YN/b001.dump\n+ echo upload_progress: 1.4KB\nupload_progress: 1.4KB\n+ echo upload_progress: done\nupload_progress: done\n+ set +x\nFinished: Tue Feb 5 11:57:33 UTC 2013","public_url":"https://s3.amazonaws.com/hkpgbackups/app10062080@heroku.com/b001.dump?AWSAccessKeyId=AKIAIYZ2BP3RBVXEIZDA&Expires=1360066058&Signature=tPwUgNg%2FR%2FtQfr2RR0eg0Kg26I4%3D","name":"b001"},"db":{"id":91769,"app_name":"data-services-1b0699f5","color":"GREEN","name":"dry-stream-40","created_at":"2012-12-14T17:16:00Z","updated_at":"2012-12-14T17:16:10Z","slug":"dry-stream-40","plan":"dev","queries_count":0,"user_id":2936,"resource_id":"resource1607206@heroku.com","encrypted_url":"O6U1HrbxsyQuIY+7ItLed2Q3cXkcqvRibtJAvV1EiByls7siZLhH3Z30e2ArWxoknTDn+V1z8oBMYcuncNmUm6U4pWwt+QZtsweSiDm2IzcM+AH0myeWPTftoMg6kEBEok/iSdiLQXP+Yq9QPIPm++LPcmoMbSRL+Ir/0IL7IgQ=--h5JN/gksRA5JaZE4Y2iX+g==","config_vars":{"PGBACKUPS_URL":"https://352020:1wxcepllftdgwc8xtdvqnm4bd@pgbackups.herokuapp.com/client","DATABASE_URL":"postgres://hievfyvexcldct:yDaDoSdZZ_58EjHEWWyF9H6y5V@ec2-54-243-178-223.compute-1.amazonaws.com:5432/dhtvgtlef75e9","HEROKU_POSTGRESQL_GREEN_URL":"postgres://hievfyvexcldct:yDaDoSdZZ_58EjHEWWyF9H6y5V@ec2-54-243-178-223.compute-1.amazonaws.com:5432/dhtvgtlef75e9"},"pg_dbs":{"postgres://hievfyvexcldct:yDaDoSdZZ_58EjHEWWyF9H6y5V@ec2-54-243-178-223.compute-1.amazonaws.com:5432/dhtvgtlef75e9":{"color_url":"HEROKU_POSTGRESQL_GREEN","color":"GREEN","url":"postgres://hievfyvexcldct:yDaDoSdZZ_58EjHEWWyF9H6y5V@ec2-54-243-178-223.compute-1.amazonaws.com:5432/dhtvgtlef75e9","sha":"583ceabdf383c1dd0fd35d89d1999d959ebfc4fe66f9bc3dc3c486ce595b6a10","connect":"psql -h ec2-54-243-178-223.compute-1.amazonaws.com -U hievfyvexcldct -d dhtvgtlef75e9 -W ","host":"ec2-54-243-178-223.compute-1.amazonaws.com","database":"dhtvgtlef75e9","user":"hievfyvexcldct","pass":"yDaDoSdZZ_58EjHEWWyF9H6y5V","port":"5432"}},"pg_db":{"color_url":"HEROKU_POSTGRESQL_GREEN","color":"GREEN","url":"postgres://hievfyvexcldct:yDaDoSdZZ_58EjHEWWyF9H6y5V@ec2-54-243-178-223.compute-1.amazonaws.com:5432/dhtvgtlef75e9","sha":"583ceabdf383c1dd0fd35d89d1999d959ebfc4fe66f9bc3dc3c486ce595b6a10","connect":"psql -h ec2-54-243-178-223.compute-1.amazonaws.com -U hievfyvexcldct -d dhtvgtlef75e9 -W ","host":"ec2-54-243-178-223.compute-1.amazonaws.com","database":"dhtvgtlef75e9","user":"hievfyvexcldct","pass":"yDaDoSdZZ_58EjHEWWyF9H6y5V","port":"5432"},"conn":{"port":"5432","color_url":"HEROKU_POSTGRESQL_GREEN","color":"GREEN","url":"postgres://hievfyvexcldct:yDaDoSdZZ_58EjHEWWyF9H6y5V@ec2-54-243-178-223.compute-1.amazonaws.com:5432/dhtvgtlef75e9","sha":"583ceabdf383c1dd0fd35d89d1999d959ebfc4fe66f9bc3dc3c486ce595b6a10","connect":"psql -h ec2-54-243-178-223.compute-1.amazonaws.com -U hievfyvexcldct -d dhtvgtlef75e9 -W ","host":"ec2-54-243-178-223.compute-1.amazonaws.com","database":"dhtvgtlef75e9","user":"hievfyvexcldct","pass":"yDaDoSdZZ_58EjHEWWyF9H6y5V"},"app_created_at":"2012-12-14T17:16:00Z","db_created_at":"2012-12-14T17:16:00Z","data_services":true}}

    def restore_backup(self, database_id, backup_id):
        self.connection.request('/api/dbs/%s/backup/b001/restore' % (database_id, backup_id), method='POST')

    def destroy_backup(self, backup_id):
        self.connection.request('/api/dbs/%s/backup/b001/destroy' % (database_id, backup_id), method='POST')
        # {"success":"OK","backup":{"name":"b001","status":"destroyed","result":"ok"}}

