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

secretId = str()
orgId = str()

class secret(object):

    """
    Secret Resource
    """

    def __init__(self, action, payload=None, secret_id=None, filters=None):

        if payload is None:
            payload = {}

        def add_secret(uri):
            return secret.Secret(self, method='post', uri=uri)

        def edit_secret(uri):
            return secret.Secret(self, method='put', uri=uri)

        def delete_secret(uri):
            return secret.Secret(self, method='delete', uri=uri)

        def get_secret(uri):
            return secret.Secret(self, method='get', uri=uri)

        def getv2_secret(uri):
            return secret.Secret(self, method='getv2', uri=uri, filters=filters)

        def get_secret_id_secret(uri):
            return secret.Secret(self, method='get', uri=uri)

        _function_mapping = {
            'add': add_secret,
            'edit':edit_secret,
            'delete':delete_secret,
            'get':get_secret,
            'getv2': getv2_secret,
            'get_secret_id': get_secret_id_secret
        }

        self.uri = {
            add_secret: 'api/v1/secret',
            get_secret: 'api/v1/secret',
            edit_secret: 'api/v1/secret/{secretId}',
            delete_secret: 'api/v1/secret/{secretId}',
            get_secret_id_secret: 'api/v1/secret/{secretId}',
            getv2_secret: 'api/v2/secret'
        }

        self.payload = resourcePaylod.Secret(payload).__dict__

        self.secretId = secret_id
        self.orgId = orch.id

        self.Response = Response()

        _wrapper_fun = _function_mapping[action]
        args = '{}_secret'.format(action)
        _wrapper_fun(self.uri[eval(args)])

    def __del__(self):
        self.payload = dict()
        self.Response = Response()


    def Secret(self, method, uri, filters=None):

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

def add(name, filename, type="Opaque"):
    return secret(action='add', payload=locals())

def edit(secret_id, name=None, filename=None):
    resp = secret(action='get_secret_id', secret_id=secret_id)
    name = resp.Response.output['name'] if name is None else name
    filename = resp.Response.output['data'] if filename is None else filename
    return secret(action='edit', secret_id=secret_id, payload=locals())

def delete(secret_id):
    return secret(action='delete', secret_id=secret_id)

def get(secret_id=None):
    if secret_id is not None:
        return secret(action='get_secret_id', secret_id=secret_id)
    else:
        return secret(action='get')

def getv2(filters=None):
    return secret(action='getv2', filters=filters)