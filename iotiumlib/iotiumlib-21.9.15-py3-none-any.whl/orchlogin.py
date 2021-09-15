"""
// ========================================================================
// Copyright (c) 2018-2020 Iotium, Inc.
// ------------------------------------------------------------------------
// All rights reserved.
//
// ========================================================================
"""

__author__ = "Rashtrapathy"
__copyright__ = "Copyright (c) 2018-2020 by Iotium, Inc."
__license__ = "All rights reserved."
__email__ = "rashtrapathy.c@iotium.io"

ip = str()
token = str()
id = str()

from iotiumlib.requires.resourcePayload import *
from iotiumlib.requires.commonWrapper import *

class orchlogin(object):

    def __init__(self, action, payload=None):

        if payload is None:
            payload = {}

        def login_orch(uri):
            return orchlogin.ORCH(self, method='post', uri=uri)

        def logout_orch(uri):
            return orchlogin.ORCH(self, method='post', uri=uri)

        _function_mapping = {
            'login': login_orch,
            'logout': logout_orch,
        }

        self.uri = {
            login_orch: 'api/v1/authenticate',
            logout_orch: 'api/v1/logout',
        }

        self.payload = resourcePaylod.Orch(payload).__dict__

        self.orgId = orch.id

        self.Response = Response()

        _wrapper_fun = _function_mapping[action]
        args = '{}_orch'.format(action)
        _wrapper_fun(self.uri[eval(args)])

    def __del__(self):
        self.payload = dict()
        self.Response = Response()

    def ORCH(self, method, uri):

        respOp = dict()
        paramRequired = checkforUriParam(uri)
        if paramRequired:
            for param in paramRequired:
                uri = re.sub(r'{{{}}}'.format(param), eval('self.{}'.format(param)), uri)

        if method == 'get':
            respOp = getApi(formUri(uri))
        elif method == 'getv2':
            self.Response = getApiv2(formUri(uri))
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


def login(username, password, otp=None):
    return orchlogin(action='login', payload=locals())


def logout():
    return orchlogin(action='logout')