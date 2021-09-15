"""
// ========================================================================
// Copyright (c) 2018-2019 Iotium, Inc.
// ------------------------------------------------------------------------
// All rights reserved.
//
// ========================================================================
"""

__author__ = "rashtrapathy.c@iotium.io"
__copyright__ = "Copyright (c) 2018-2019 by Iotium, Inc."
__license__ = "All rights reserved."

from iotiumlib.requires.commonWrapper import *
from iotiumlib.requires.resourcePayload import *

firewallgroupId = str()
orgId = str()

class firewallgroup(object):

    """
    FWG Resource
    """

    def __init__(self, action, payload=None, filters=None, firewallgroup_id=None):

        if payload is None:
            payload = {}

        def add_fwg(uri):
            return firewallgroup.FWG(self, method='post', uri=uri)

        def edit_fwg(uri):
            return firewallgroup.FWG(self, method='put', uri=uri)

        def delete_fwg(uri):
            return firewallgroup.FWG(self, method='delete', uri=uri)

        def get_fwg(uri):
            return firewallgroup.FWG(self, method='get', uri=uri)

        def get_fwg_id_fwg(uri):
            return firewallgroup.FWG(self, method='get', uri=uri)

        def getv2_fwg(uri):
            return firewallgroup.FWG(self, method='getv2', uri=uri, filters=filters)

        _function_mapping = {
            'add': add_fwg,
            'edit':edit_fwg,
            'delete':delete_fwg,
            'get':get_fwg,
            'get_fwg_id': get_fwg_id_fwg,
            'getv2': getv2_fwg
        }

        self.uri = {
            add_fwg: 'api/v1/firewallgroup',
            get_fwg: 'api/v1/firewallgroup',
            edit_fwg: 'api/v1/firewallgroup/{firewallgroupId}',
            delete_fwg: 'api/v1/firewallgroup/{firewallgroupId}',
            get_fwg_id_fwg: 'api/v1/firewallgroup/{firewallgroupId}',
            getv2_fwg: 'api/v2/firewallgroup',
        }

        self.payload = resourcePaylod.FWG(payload).__dict__

        self.firewallgroupId = firewallgroup_id
        self.orgId = orch.id

        self.Response = Response()

        _wrapper_fun = _function_mapping[action]
        args = '{}_fwg'.format(action)
        _wrapper_fun(self.uri[eval(args)])

    def __del__(self):
        self.payload = dict()
        self.Response = Response()


    def FWG(self, method, uri, filters=None):

        respOp = dict()
        paramRequired = checkforUriParam(uri)
        if paramRequired:
            for param in paramRequired:
                uri = re.sub(r'{{{}}}'.format(param), eval('self.{}'.format(param)), uri)
        try:
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
        except (ApiPayloadError, ApiMethodError) as errMsg:
            print(errMsg)

def add(name, org_id, label=None, **rules):

    """

    :param name:
    :param org_id:
    :param label:
    :param rules:
    :return:
    """
    return firewallgroup(action='add', payload=locals())

def edit(firewallgroup_id, name=None, label=None, **edit_rules):

    resp = firewallgroup(action='get_fwg_id', firewallgroup_id=firewallgroup_id)

    rules={"rules":[]}

    if resp.Response.code == 200:
        name = resp.Response.output['name'] if name is None else name
        org_id = resp.Response.output['organization']['id']
        if label is None:
            labels = []
            for k, v in resp.Response.output['metadata']['labels'].items():
                if not k.startswith('_'):
                    labels.append(":".join([k.strip(), v.strip()]))
            label = str(', '.join(labels))

        index=0
        from operator import itemgetter
        for rule in sorted(resp.Response.output['rules'], key=itemgetter('priority')):
            rules['rules'].append({})
            rules['rules'][index].update({"source_cidr":rule['source_ip']})
            rules['rules'][index].update({"destination_cidr":rule['destination_ip']})
            rules['rules'][index].update({"action":rule['action']})
            rules['rules'][index].update({"priority":rule['priority']})
            rules['rules'][index].update({"protocol":rule['protocol']})

            if 'destination_network' in rule:
                to_network = ""
                for k,v in rule['destination_network'].items():
                    if (k.find('network.')) != -1:
                        to_network="{}={}".format(k[k.find('network.') + len('network.'):], v)
                    else:
                        to_network = "{}={}:{}".format("label", k, v)
                rules['rules'][index].update({"to_network": to_network})

            if 'source_network' in rule:
                from_network = ""
                for k,v in rule['source_network'].items():
                    if (k.find('network.')) != -1:
                        from_network="{}={}".format(k[k.find('network.') + len('network.'):], v)
                    else:
                        from_network = "{}={}:{}".format("label", k,v)
                rules['rules'][index].update({"from_network": from_network})

            index+=1

        sorted(rules['rules'], key=itemgetter('priority'))
        index=0
        for each_edit in edit_rules['rules']:
            if 'from_network' in each_edit:
                rules['rules'][index]['from_network'] = each_edit['from_network']
            if 'to_network' in each_edit:
                rules['rules'][index]['to_network'] = each_edit['to_network']
            if 'protocol' in each_edit:
                rules['rules'][index]['protocol'] = each_edit['protocol']
            if 'priority' in each_edit:
                rules['rules'][index]['priority'] = each_edit['priority']
            if 'action' in each_edit:
                rules['rules'][index]['action'] = each_edit['action']
            if 'destination_cidr' in each_edit:
                rules['rules'][index]['destination_cidr'] = each_edit['destination_cidr']
            if 'source_cidr' in each_edit:
                rules['rules'][index]['source_cidr'] = each_edit['source_cidr']
            index+=1

    return firewallgroup(action='edit', payload=locals(), firewallgroup_id=firewallgroup_id)

def delete(firewallgroup_id):
    return firewallgroup(action='delete', firewallgroup_id=firewallgroup_id)

def get(firewallgroup_id=None):
    if firewallgroup_id is not None:
        return firewallgroup(action='get_fwg_id', firewallgroup_id=firewallgroup_id)
    else:
        return firewallgroup(action='get')

def getv2(filters=None):
    return firewallgroup(action='getv2', filters=filters)
