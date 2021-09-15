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

from .requires.commonWrapper import *
from .requires.resourcePayload import *

nodeId = str()
orgId = str()

class image(object):
    __class__ = "iNodeIimage"

    """
    iNodeImage Resource
    """

    def __init__(self, action, filters=None, payload=None, node_id=None, image_id=None):

        if payload is None:
            payload = {}

        def delete_image(uri):
            return image.IMAGE(self, method='delete', uri=uri)

        def getv2_image(uri):
            return image.IMAGE(self, method='getv2', uri=uri, filters=filters)

        _function_mapping = {
            'delete': delete_image,
            'getv2': getv2_image,
        }

        self.uri = {
            delete_image: 'api/v1/node/{nodeId}/image/{imageId}',
            getv2_image: 'api/v2/node/{nodeId}/image'
        }

        self.payload = resourcePaylod.IMAGE(payload).__dict__

        self.nodeId = node_id
        self.imageId = image_id
        self.orgId = id

        self.Response = Response()

        _wrapper_fun = _function_mapping[action]
        args = '{}_image'.format(action)
        _wrapper_fun(self.uri[eval(args)])

    def __del__(self):
        self.payload = dict()
        self.Response = Response()

    def IMAGE(self, method, uri, filters=None):

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


def delete(node_id, image_id):
    return image(action="delete",
                 image_id=image_id,
                 node_id=node_id
                 )


def getv2(node_id, filters=None):
    return image(filters=filters,
                 node_id=node_id,
                 action='getv2')
