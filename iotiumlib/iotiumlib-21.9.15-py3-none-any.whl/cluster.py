"""
// ========================================================================
// Copyright (c) 2020-2021 Iotium, Inc.
// ------------------------------------------------------------------------
// All rights reserved.
//
// ========================================================================
"""

__author__ = "Rashtrapathy"
__copyright__ = "Copyright (c) 2020 by Iotium, Inc."
__license__ = "All rights reserved."
__email__ = "rashtrapathy.c@iotium.io"

from iotiumlib.requires.commonWrapper import *
from iotiumlib.requires.resourcePayload import *

clusterId = str()


class cluster(object):
    def __init__(self, action, payload=None, filters=None, cluster_id=None):

        if payload is None:
            payload = {}

        def get_cluster(uri):
            return cluster.Cluster(self, method='get', uri=uri)

        def getv2_cluster(uri):
            return cluster.Cluster(self, method='getv2', uri=uri, filters=filters)

        def add_cluster(uri):
            return cluster.Cluster(self, method='post', uri=uri)

        def edit_cluster(uri):
            return cluster.Cluster(self, method='put', uri=uri)

        def delete_cluster(uri):
            return cluster.Cluster(self, method='delete', uri=uri)

        _function_mapping = {
            'get': get_cluster,
            'getv2': getv2_cluster,
            'add': add_cluster,
            'edit': edit_cluster,
            'delete': delete_cluster
        }

        self.uri = {
            get_cluster: 'api/v1/cluster/{clusterId}',
            getv2_cluster: 'api/v2/cluster',
            add_cluster: 'api/v1/cluster',
            edit_cluster: 'api/v1/cluster/{clusterId}',
            delete_cluster: 'api/v1/cluster/{clusterId}'
        }

        self.payload = resourcePaylod.Cluster(payload).__dict__

        self.clusterId = cluster_id

        self.Response = Response()

        _wrapper_fun = _function_mapping[action]
        args = '{}_cluster'.format(action)
        _wrapper_fun(self.uri[eval(args)])

    def Cluster(self, method, uri, filters=None):

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
    def add(name, labels=None, nodes=None, container_timezone=None, instance_id=100):
        return cluster(action='add', payload=locals())

    @staticmethod
    def edit(cluster_id, name=None, labels=None, nodes=None, container_timezone=None, instance_id=None):
        resp = cluster.get(cluster_id=cluster_id)

        name = resp.Response.output['name'] if name is None else name

        if instance_id is None:
            if 'config' in resp.Response.output and 'instance_id' in resp.Response.output['config']:
                instance_id = resp.Response.output['config']['instance_id']
        else:
            instance_id =  instance_id

        if nodes is None:
            nodes = []
            if 'nodes' in resp.Response.output:
                for n in resp.Response.output['nodes']:
                    node_id = str()
                    priority = int()
                    is_candidate = bool()
                    if 'node' in n:
                        node_id = n['node']['id']

                    if 'config' in n:
                        priority = n['config']['priority']
                        is_candidate = n['config']['is_candidate']
                    nodes.append({"node_id": node_id, "priority": priority, "is_candidate": is_candidate})

        return cluster(action='edit', payload=locals(), cluster_id=cluster_id)

    @staticmethod
    def delete(cluster_id):
        return cluster(action='delete', cluster_id=cluster_id)

    @staticmethod
    def getv2(filters=None):
        return cluster(action='getv2', filters=filters)

    @staticmethod
    def get(cluster_id):
        return cluster(action='get', cluster_id=cluster_id)
