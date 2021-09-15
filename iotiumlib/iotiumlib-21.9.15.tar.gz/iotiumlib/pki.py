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

class pki(object):
    def __init__(self, action, filters=None, payload=None, org_id=None):

        if payload is None:
            payload = {}
        self.payload = dict()
        self.resp = Response()

        def get_pki(uri):
            return pki.Pki(self, method='get', uri=uri)

        def getv2_pki(uri):
            return pki.Pki(self, method='getv2', uri=uri, filters=filters)

        _function_mapping = {
            'get':get_pki,
            'getv2': getv2_pki,
        }

        self.uri = {
            get_pki: 'api/v1/pki',
            getv2_pki:'api/v2/pki',
        }

        self.payload = resourcePaylod.Organisation(payload).__dict__

        self.orgId = orch.id

        self.Response = Response()

        _wrapper_fun = _function_mapping[action]
        args = '{}_pki'.format(action)
        _wrapper_fun(self.uri[eval(args)])

    def Pki(self, method, uri, filters=None):
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
    return pki(action='get')

def getv2(filters=None):
    return pki(filters=filters, action='getv2')
