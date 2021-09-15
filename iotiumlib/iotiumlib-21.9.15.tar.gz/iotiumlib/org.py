"""
// ========================================================================
// Copyright (c) 2018-2019 Iotium, Inc.
// ------------------------------------------------------------------------
// All rights reserved.
//
// ========================================================================
"""

__author__ = "Rashtrapathy"
__copyright__ = "Copyright (c) 2018-2019 by Iotium, Inc."
__license__ = "All rights reserved."
__email__ = "rashtrapathy.c@iotium.io"

from iotiumlib.requires.commonWrapper import *
from iotiumlib.requires.resourcePayload import *

orgId = str()

class org(object):
    def __init__(self, action, payload=None, org_id=None, filters=None):

        if payload is None:
            payload = {}

        def get_org(uri):
            return org.Org(self, method='get', uri=uri)

        def getv2_org(uri):
            return org.Org(self, method='getv2', uri=uri, filters=filters)

        def get_org_name_org(uri):
            return org.Org(self, method='get', uri=uri)

        def get_org_id_org(uri):
            return org.Org(self, method='get', uri=uri)

        def add_org(uri):
            return org.Org(self, method='post', uri=uri)

        def edit_org(uri):
            return org.Org(self, method='put', uri=uri)

        def delete_org(uri):
            return org.Org(self, method='delete', uri=uri)

        def policy_org(uri):
            return org.Org(self, method='post', uri=uri)

        _function_mapping = {
            'get' : get_org,
            'getv2': getv2_org,
            'add' : add_org,
            'edit' : edit_org,
            'delete':delete_org,
            'get_org_id': get_org_id_org,
            'get_org_name': get_org_name_org,
            'policy': policy_org,
        }

        self.uri = {
            get_org: 'api/v1/org',
            get_org_name_org:'api/v1/user/current',
            getv2_org: 'api/v2/org',
            add_org: 'api/v1/org',
            edit_org: 'api/v1/org/{orgId}',
            delete_org: 'api/v1/org/{orgId}',
            get_org_id_org: 'api/v1/org/{orgId}',
            policy_org: 'api/v1/org/{orgId}/policy',
        }

        if action == "policy":
            self.payload = resourcePaylod.OrgPolicy(payload).__dict__
        else:
            self.payload = resourcePaylod.Organisation(payload).__dict__

        self.orgId = org_id

        self.Response = Response()

        _wrapper_fun = _function_mapping[action]
        args = '{}_org'.format(action)
        _wrapper_fun(self.uri[eval(args)])

    def Org(self, method, uri, filters=None):

        respOp = dict()
        paramRequired = checkforUriParam(uri)
        if paramRequired:
            for param in paramRequired:
                uri = re.sub(r'{{{}}}'.format(param), eval('self.{}'.format(param)), uri)

        if method == 'get':
            respOp = getApi(formUri(uri))
        elif method == 'getv2':
            self.Response = getApiv2(formUri(uri), filters)
            return self.Response
        elif method == 'post':
            respOp = postApi(formUri(uri), self.payload)
        elif method == 'put':
            respOp = putApi(formUri(uri), self.payload)
        elif method == 'delete':
            respOp = deleteApi(formUri(uri))
        else:
            return self.Response
        self.Response.output = respOp.json()
        self.Response.code = respOp.status_code
        return self.Response

def get(org_id=""):
    if org_id is not None:
        return org(action='get_org_id', org_id=org_id)
    elif org_id is None:
        return org(action='get_org_name')
    else:
        return org(action='get')

def getv2(filters=None):
    return org(action='getv2', filters=filters)

def add(org_name, billing_name, billing_email,
        domain_name="", timezone=""):
    return org(action="add", payload=locals())

def edit(org_id, org_name=None, billing_name=None, billing_email=None,
        domain_name=None, timezone=None):

    resp = get(org_id=org_id)

    org_name = resp.Response.output['name'] if org_name is None else org_name
    billing_name = resp.Response.output['billing_name'] if billing_name is None else billing_name
    billing_email = resp.Response.output['billing_email']['stat_mode'] if billing_email is None else billing_email
    domain_name = resp.Response.output['domain_name'] if domain_name is None else domain_name
    timezone = resp.Response.output['timezone'] if timezone is None else timezone

    return org(action="edit", payload=locals())

def delete(org_id):
    return org(action="delete", org_id= org_id, payload=locals())

def policy(org_id, two_factor=None, headless_mode=None, vlan_support=None, software_upgrade_channel=None,
           apikey=None, one_arm_mode=None, branding=None, cluster=None):
    return org(action="policy", org_id= org_id, payload=locals())
