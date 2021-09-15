"""
// ========================================================================
// Copyright (c) 2018-2019 Iotium, Inc.
// ------------------------------------------------------------------------
// All rights reserved.
//
// ========================================================================
"""
__author__ = "Rashtrapathy"
__copyright__ = "Copyright (c) 2020 by Iotium, Inc."
__license__ = "All rights reserved."
__email__ = "rashtrapathy.c@iotium.io"

import re


def get_resource_by_label(resource, labelname):
    resource_name_list = []

    reObjLabel = re.compile('.+?Label')

    resource_details_op = resource.getv2().Response.formattedOutput

    if not resource_details_op:
        return False

    for n in resource_details_op:
        resource_dict = dict()
        for key in list(n.keys()):
            if reObjLabel.match(key):
                for l in n[key].split(','):
                    if l == labelname:
                        keyList = list(n.keys())
                        for i, item in enumerate(keyList):
                            if re.search('{}.+?'.format(resource.__name__.rsplit('.')[1]), item.lower()):
                                resource_dict.update({item: n[item]})
                        resource_name_list.append(resource_dict)
    return resource_name_list


def get_resource_id_by_name(resource, name):
    resourceId = str()
    resource_details_op = resource.getv2().Response.output
    if resource_details_op:
        try:
            itemList = next((item for item in resource_details_op if item["name"] == name))
            resourceId = itemList['id']
            return str(resourceId)
        except StopIteration as E:
            return resourceId
    else:
        return resourceId


def get_all_networks_from_node(name):
    from iotiumlib import node

    str1 = list(dict())

    node_details_op = node.getv2().Response.output
    if node_details_op is False:
        return False
    try:
        itemList = next((item for item in node_details_op if item["name"] == name))
    except StopIteration:
        return False

    if 'networks' in itemList:
        for network in itemList['networks']:
            if network['name']:
                networkId = network['id']
                networkName = network['name']
                str1.append({networkName: networkId})
        return str1


def get_resource_name_by_id(resource, id):
    resourceName = str()
    resource_details_op = resource.getv2().Response.output
    if resource_details_op:
        try:
            itemList = next((item for item in resource_details_op if item["id"] == id))
            resourceName = itemList['name']
            return str(resourceName)
        except StopIteration as E:
            return resourceName
    else:
        return resourceName


def get_master_inode(cluster_id):

    from iotiumlib import cluster

    str1 = list(dict())
    resp = cluster.getv2().Response.output

    if resp:
        try:
            itemList = next((item for item in resp if item["id"] == cluster_id))
        except StopIteration:
            return str1

        if 'status' in itemList:
            for master_node in itemList['status'].values():
                for m in master_node:
                    if m['state'] == "MASTER":
                        for all_node in itemList['nodes']:
                            if all_node['node']['id'] == m['id']:
                                str1.append({all_node['node']['name']: {"id": m["id"],
                                                       "is_candidate": all_node['config']['is_candidate'],
                                                       "priority": all_node['config']['priority']}})
            return str1
        else:
            return str1
    else:
        return str1

def get_all_networks_from_cluster(cluster_id):

    from iotiumlib import network

    resp = network.getv2(filters={"cluster_id":cluster_id}).Response

    op = list()

    if resp.output:
        for network in resp.output:
            print(network)
            res = dict()
            res.update({'id':network['id'], 'name':network['name']})
            if 'is_wan_network' in network and network['is_wan_network']:
                res.update({'wan':True})
            op.append(res)

    return op

def get_backup_inode(cluster_id):

    from iotiumlib import cluster

    str1 = list(dict())
    resp = cluster.getv2().Response.output

    if resp:
        try:
            itemList = next((item for item in resp if item["id"] == cluster_id))
        except StopIteration:
            return str1

        if 'status' in itemList:
            for master_node in itemList['status'].values():
                for m in master_node:
                    if m['state'] == "BACKUP":
                        for all_node in itemList['nodes']:
                            if all_node['node']['id'] == m['id']:
                                str1.append({all_node['node']['name']: {"id": m["id"],
                                                       "is_candidate": all_node['config']['is_candidate'],
                                                       "priority": all_node['config']['priority']}})
            return str1
        else:
            return str1
    else:
        return str1


