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

nodeId = str()
orgId = str()


class node(object):
    __class__ = "iNode"

    """
    iNode Resource
    """

    def __init__(self, action, filters=None, payload=None, node_id=None):

        if payload is None:
            payload = {}

        def add_inode(uri):
            return node.iNode(self, method='post', uri=uri)

        def edit_inode(uri):
            return node.iNode(self, method='put', uri=uri)

        def delete_inode(uri):
            return node.iNode(self, method='delete', uri=uri)

        def get_inode(uri):
            return node.iNode(self, method='get', uri=uri)

        def getv2_inode(uri):
            return node.iNode(self, method='getv2', uri=uri, filters=filters)

        def get_node_id_inode(uri):
            return node.iNode(self, method='get', uri=uri)

        def reboot_inode(uri):
            return node.iNode(self, method='post', uri=uri)

        def notifications_inode(uri):
            return node.Notifications(self, method='notifications', uri=uri, filters=filters)

        def stats_inode(uri):
            return node.Stats(self, method='stats', uri=uri, filters=filters)

        def statssummary_inode(uri):
            return node.Stats(self, method='stats', uri=uri, filters=filters)

        _function_mapping = {
            'add': add_inode,
            'edit': edit_inode,
            'delete': delete_inode,
            'get': get_inode,
            'reboot': reboot_inode,
            'get_node_id': get_node_id_inode,
            'getv2': getv2_inode,
            'notifications': notifications_inode,
            'stats':stats_inode,
            'statssummary':statssummary_inode
        }

        self.uri = {
            add_inode: 'api/v1/node',
            get_inode: 'api/v1/node',
            getv2_inode: 'api/v2/node',
            edit_inode: 'api/v1/node/{nodeId}',
            delete_inode: 'api/v1/node/{nodeId}',
            get_node_id_inode: 'api/v1/node/{nodeId}',
            reboot_inode: 'api/v1/node/{nodeId}/reboot',
            notifications_inode:'api/v2/notification/node/{nodeId}/event',
            stats_inode:'api/v1/report/node/{nodeId}/stats',
            statssummary_inode: 'api/v1/report/node/{nodeId}/stats',
        }

        self.payload = resourcePaylod.iNode(payload).__dict__

        self.nodeId = node_id
        self.orgId = orch.id

        self.Response = Response()

        _wrapper_fun = _function_mapping[action]
        args = '{}_inode'.format(action)
        _wrapper_fun(self.uri[eval(args)])

    def __del__(self):
        self.payload = dict()
        self.Response = Response()

    def iNode(self, method, uri, filters=None):

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

    def Notifications(self, method, uri, filters=None):
        paramRequired = checkforUriParam(uri)
        if paramRequired:
            for param in paramRequired:
                uri = re.sub(r'{{{}}}'.format(param), eval('self.{}'.format(param)), uri)
        if method == 'notifications':
            self.Response = getApiv2(formUri(uri), filters)
            return self.Response

    def Stats(self, method, uri, filters=None):
        paramRequired = checkforUriParam(uri)
        if paramRequired:
            for param in paramRequired:
                uri = re.sub(r'{{{}}}'.format(param), eval('self.{}'.format(param)), uri)
        if method == 'stats':
            respOp = getApi(formUri(uri))
        elif method == 'statssummary':
            respOp = getApi(formUri(uri))
        else:
            return self.Response
        self.Response.output = respOp.json()
        self.Response.code = respOp.status_code
        return self.Response

def add(inode_name, serial_number, profile_id, org_id, standalone_expires=0, label=None, data_saving_mode="Fast", ssh_keys=None, container_timezone=None):
    """
    Add iNode
    :param data_saving_mode:
    :param inode_name: iNode Name
    :param serial_number: Serial Number of Edge iNode
    :param profile_id: Profile ID of Edge/Virtual Edge/Virtual
    :param org_id: ORG ID
    :param standalone_expires:
    :param label:
    :return: resp object
    """
    return node(action="add", payload=locals())


def edit(node_id, inode_name=None, label=None, standalone_expires=0, data_saving_mode=None, ssh_keys=None, container_timezone=None):
    resp = get(node_id=node_id)
    inode_name = resp.Response.output['name'] if inode_name is None else inode_name
    standalone_expires = resp.Response.output['max_headless_time'] if standalone_expires is None else standalone_expires
    data_saving_mode = resp.Response.output['stat_config']['stat_mode'] if data_saving_mode is None else data_saving_mode
    if ssh_keys is None and 'ssh_keys' in resp.Response.output:
        ssh_keys = resp.Response.output['ssh_keys'][0]['id']

    if label is None:
        labels = []
        for k, v in resp.Response.output['metadata']['labels'].items():
            if not k.startswith('_'):
                labels.append(":".join([k.strip(), v.strip()]))
        label = str(','.join(labels))
    elif label.title() == "None":
        label = "None"

    return node(action="edit",
                payload=locals(),
                node_id=node_id
                )


def delete(node_id):
    return node(action="delete",
                node_id=node_id
                )


def reboot(node_id):
    return node(action="reboot",
                node_id=node_id
                )


def get(node_id=None):
    if node_id is not None:
        return node(action='get_node_id', node_id=node_id)
    else:
        return node(action="get")


def getv2(filters=None):
    return node(filters=filters, action='getv2')

def notifications(node_id, type=None, filters=None):

    if filters is None:
        filters = dict()

    if type:
        filters.update({'type':type})

    return node(node_id=node_id, action="notifications", filters=filters)

def stats(node_id):
    return node(node_id=node_id, action="stats")

def statssummary(node_id):
    return node(node_id=node_id, action="statssummary")