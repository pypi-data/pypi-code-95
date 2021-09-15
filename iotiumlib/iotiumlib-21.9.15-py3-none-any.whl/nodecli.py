"""
// ========================================================================
// Copyright (c) 2021 Iotium, Inc.
// ------------------------------------------------------------------------
// All rights reserved.
//
// ========================================================================
"""

__author__ = "Rashtrapathy"
__copyright__ = "Copyright (c) 2021 by Iotium, Inc."
__license__ = "All rights reserved."
__email__ = "rashtrapathy.c@iotium.io"

from iotiumlib.requires.commonWrapper import *
from iotiumlib.requires.resourcePayload import *

nodeId = str()
Command = str()


class nodecli(object):
    def __init__(self, action, payload=None, filters=None, node_id=None, command=None):

        if payload is None:
            payload = {}

        def set_nodecli(uri):
            return nodecli.iNodeCli(self, method='post', uri=uri)

        def unset_nodecli(uri):
            return nodecli.iNodeCli(self, method='post', uri=uri)

        _function_mapping = {
            'set': set_nodecli,
            'unset': set_nodecli
        }

        self.uri = {
            set_nodecli: 'api/v1/node/{nodeId}/{Command}',
            unset_nodecli: 'api/v1/node/{nodeId}/{Command}',
        }

        self.payload = resourcePaylod.iNodeCli(action, payload).__dict__

        self.nodeId = node_id
        self.Command = command

        self.Response = Response()

        _wrapper_fun = _function_mapping[action]
        args = '{}_nodecli'.format(action)
        _wrapper_fun(self.uri[eval(args)])

    def iNodeCli(self, method, uri, filters=None):

        respOp = dict()
        paramRequired = checkforUriParam(uri)
        if paramRequired:
            for param in paramRequired:
                uri = re.sub(r'{{{}}}'.format(param), eval('self.{}'.format(param)), uri)

        if method == 'post':
            respOp = postApi(formUri(uri), self.payload)
        else:
            return self.Response
        self.Response.output = respOp.json()
        self.Response.code = respOp.status_code
        return self.Response

    @staticmethod
    def set(node_id, command, params):
        return nodecli(action='set', payload=locals(), node_id=node_id, command=command)

    @staticmethod
    def unset(node_id, command, params):
        return nodecli(action='unset', payload=locals(), node_id=node_id, command=command)
