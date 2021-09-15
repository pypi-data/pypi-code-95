"""
// ========================================================================
// Copyright (c) 2018-2019 Iotium, Inc.
// ------------------------------------------------------------------------
// All rights reserved.
//
// ========================================================================
"""


__author__ = "ioTium QA"
__copyright__ = "Copyright (c) 2018-2019 by Iotium, Inc."
__license__ = "All rights reserved."

from iotiumlib.requires.commonWrapper import *
from iotiumlib.requires.resourcePayload import *

from iotiumlib import orch

orgId = str()


class profile(object):
    def __init__(self, action, filters=None):

        self.orgId = orch.id

        self.payload = dict()
        self.Response = Response()

        def get_profile(uri):
            return profile.getProfile(self, method='get', uri=uri)

        def getv2_profile(uri):
            return profile.getProfile(self, method='getv2', uri=uri, filters=filters)

        _function_mapping = {
            'get':get_profile,
            'getv2':getv2_profile,
        }

        self.uri = {
            get_profile: 'api/v1/profile',
            getv2_profile:'api/v2/profile'
        }

        _wrapper_fun = _function_mapping[action]
        args = '{}_profile'.format(action)
        _wrapper_fun(self.uri[eval(args)])

    def getProfile(self, method, uri, filters=None):

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

def get():
    return profile(action='get')

def getv2(filters=None):
    return profile(action='getv2', filters=filters)