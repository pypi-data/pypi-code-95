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

import copy

from tempest.lib.api_schema.response.compute.v2_1 import limits as limitv21

# Compute microversion 2.36:
# remove attributes in get_limit:
#    'maxSecurityGroupRules',
#    'maxSecurityGroups',
#    'maxTotalFloatingIps',
#    'totalFloatingIpsUsed',
#    'totalSecurityGroupsUsed'

get_limit = copy.deepcopy(limitv21.get_limit)

for item in ['maxSecurityGroupRules', 'maxSecurityGroups',
             'maxTotalFloatingIps', 'totalFloatingIpsUsed',
             'totalSecurityGroupsUsed']:
    get_limit['response_body']['properties']['limits']['properties'][
        'absolute']['properties'].pop(item)
    get_limit['response_body']['properties']['limits']['properties'][
        'absolute']['required'].remove(item)
