"""
// ========================================================================
// Copyright (c) 2020-2021 Iotium, Inc.
// ------------------------------------------------------------------------
// All rights reserved.
//
// ========================================================================
"""

__author__ = "Rashtrapathy"
__copyright__ = "Copyright (c) 2020-2021 by Iotium, Inc."
__license__ = "All rights reserved."
__email__ = "rashtrapathy.c@iotium.io"

from iotiumlib.requires.commonWrapper import *
from iotiumlib.requires.resourcePayload import *

sshkeyId = str()

class sshkey(object):
    def __init__(self, action, payload=None, filters=None, sshkey_id=None):

        if payload is None:
            payload = {}

        def getv2_sshkey(uri):
            return sshkey.SshKey(self, method='getv2', uri=uri, filters=filters)

        def add_sshkey(uri):
            return sshkey.SshKey(self, method='post', uri=uri)

        def delete_sshkey(uri):
            return sshkey.SshKey(self, method='delete', uri=uri)

        _function_mapping = {
            'getv2': getv2_sshkey,
            'add' : add_sshkey,
            'delete':delete_sshkey
        }

        self.uri = {
            getv2_sshkey: 'api/v2/sshkey',
            add_sshkey: 'api/v1/sshkey',
            delete_sshkey: 'api/v1/sshkey/{sshkeyId}'
        }

        self.payload = resourcePaylod.SshKey(payload).__dict__

        self.sshkeyId = sshkey_id

        self.Response = Response()

        _wrapper_fun = _function_mapping[action]
        args = '{}_sshkey'.format(action)
        _wrapper_fun(self.uri[eval(args)])

    def SshKey(self, method, uri, filters=None):

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

    @staticmethod
    def add(name, public_key):
        return sshkey(action='add', payload=locals())

    @staticmethod
    def delete(sshkey_id):
        return sshkey(action='delete', sshkey_id=sshkey_id)

    @staticmethod
    def getv2(filters=None):
        return sshkey(action='getv2', filters=filters)