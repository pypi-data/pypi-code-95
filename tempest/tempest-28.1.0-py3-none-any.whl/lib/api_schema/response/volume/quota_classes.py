# Copyright 2018 ZTE Corporation.  All rights reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

show_quota_classes = {
    'status_code': [200],
    'response_body': {
        'type': 'object',
        'properties': {
            'quota_class_set': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'string', 'format': 'uuid'},
                    'volumes': {'type': 'integer'},
                    'snapshots': {'type': 'integer'},
                    'backups': {'type': 'integer'},
                    'groups': {'type': 'integer'},
                    'per_volume_gigabytes': {'type': 'integer'},
                    'gigabytes': {'type': 'integer'},
                    'backup_gigabytes': {'type': 'integer'},
                },
                # for volumes_{volume_type}, etc
                "additionalProperties": {'type': 'integer'},
                'required': ['id', 'volumes', 'snapshots', 'backups',
                             'per_volume_gigabytes', 'gigabytes',
                             'backup_gigabytes'],
            }
        },
        'required': ['quota_class_set']
    }
}

update_quota_classes = {
    'status_code': [200],
    'response_body': {
        'type': 'object',
        'properties': {
            'quota_class_set': {
                'type': 'object',
                'properties': {
                    'volumes': {'type': 'integer'},
                    'snapshots': {'type': 'integer'},
                    'backups': {'type': 'integer'},
                    'groups': {'type': 'integer'},
                    'per_volume_gigabytes': {'type': 'integer'},
                    'gigabytes': {'type': 'integer'},
                    'backup_gigabytes': {'type': 'integer'},
                },
                # for volumes_{volume_type}, etc
                "additionalProperties": {'type': 'integer'},
                'required': ['volumes', 'snapshots', 'backups',
                             'per_volume_gigabytes', 'gigabytes',
                             'backup_gigabytes'],
            }
        },
        'required': ['quota_class_set']
    }
}
