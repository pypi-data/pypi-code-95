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

networkId = str()
orgId = str()

class network(object):

    """
    Network Resource
    """

    def __init__(self, action, payload=None, network_id=None, filters=None):

        if payload is None:
            payload = {}

        def add_network(uri):
            return network.Network(self, method='post', uri=uri)

        def edit_network(uri):
            return network.Network(self, method='put', uri=uri)

        def delete_network(uri):
            return network.Network(self, method='delete', uri=uri)

        def get_network(uri):
            return network.Network(self, method='get', uri=uri)

        def getv2_network(uri):
            return network.Network(self, method='getv2', uri=uri, filters=filters)

        def get_network_id_network(uri):
            return network.Network(self, method='get', uri=uri)

        def reset_counter_network(uri):
            return network.Network(self, method='post', uri=uri)

        _function_mapping = {
            'add': add_network,
            'edit':edit_network,
            'delete':delete_network,
            'get':get_network,
            'get_network_id': get_network_id_network,
            'getv2': getv2_network,
            'reset_counter':reset_counter_network
        }

        self.uri = {
            add_network: 'api/v1/network',
            get_network: 'api/v1/network',
            getv2_network: 'api/v2/network',
            edit_network: 'api/v1/network/{networkId}',
            delete_network: 'api/v1/network/{networkId}',
            get_network_id_network: 'api/v1/network/{networkId}',
            reset_counter_network: 'api/v1/network/{networkId}/resetcounter',
        }

        self.payload = resourcePaylod.Network(payload).__dict__

        self.networkId = network_id
        self.orgId = orch.id

        self.Response = Response()

        _wrapper_fun = _function_mapping[action]
        args = '{}_network'.format(action)
        _wrapper_fun(self.uri[eval(args)])

    def __del__(self):
        self.payload = dict()
        self.Response = Response()


    def Network(self, method, uri, filters=None):

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

def add(network_name, node_id=None, cluster_id=None, cidr=None, start_ip=None, gateway_ip=None, end_ip=None,
        label=None, default_destination=None,
        connect_networks=None, firewall_selector=None, vlan_id=0, network_addressing="STATIC",
        firewall_policy=False, service_addressing="AUTO", static_routes=None, interface_ip=None):

    if connect_networks is None:
        connect_networks = []
    dd = list()
    if default_destination and default_destination is not None and default_destination.title() != "None":
        dd.append({'destination': "0.0.0.0/0", 'via': default_destination})
    elif isinstance(default_destination, str) and default_destination.title() == "None":
        dd = []
    elif default_destination == None and not default_destination:
        dd = []

    default_destination = dd

    sr = list(default_destination)
    if static_routes and static_routes is not None:
        static_routes = re.sub("\s\s+" , " ", static_routes)
        for each_route in static_routes.split(' '):
            if each_route.split(",")[2:]:
                try:
                    import ipaddress
                    ipaddress.ip_network(each_route.split(",")[2:][-1], strict=False)
                    sr.append({"destination": each_route.split(",")[0], "via": each_route.split(",")[1],
                               "allow_from_virtual": each_route.split(",")[2:-1],
                               "local_representation_network":each_route.split(",")[2:][-1]})
                except ValueError:
                    sr.append({"destination": each_route.split(",")[0], "via": each_route.split(",")[1],
                               "allow_from_virtual": each_route.split(",")[2:]})
            else:
                sr.append({"destination": each_route.split(",")[0], "via": each_route.split(",")[1]})
    static_routes = sr
    del default_destination

    return network(action='add', payload=locals())


def edit(network_id, network_name=None, cidr=None, gateway_ip=None, start_ip=None, end_ip=None, label=None,
         default_destination=None, connect_networks=None, firewall_selector=None, vlan_id=None, firewall_policy=None,
         static_routes=None, interface_ip=None):

    resp = network(action='get_network_id', network_id=network_id)

    network_name = resp.Response.output['name'] if network_name is None else network_name
    if network_name != "WAN Network":
        cidr = resp.Response.output['config']['network']['cidr'] if cidr is None else cidr
        if 'gateway' in resp.Response.output['config']['network']:
            gateway_ip = resp.Response.output['config']['network']['gateway'] if gateway_ip is None else gateway_ip
        if 'tan_interface_ip' in resp.Response.output['config']['network']:
            interface_ip = resp.Response.output['config']['network']['tan_interface_ip'] if interface_ip is None else interface_ip
        if 'reserved' in resp.Response.output['config']['network']:
            start_ip = resp.Response.output['config']['network']['reserved'][0]['start'] if start_ip is None else start_ip
            end_ip = resp.Response.output['config']['network']['reserved'][0]['end'] if end_ip is None else end_ip
        vlan_id = resp.Response.output['config']['network']['vlan_id'] if vlan_id is None else vlan_id

    if label is None:
        labels=[]
        for k,v in resp.Response.output['metadata']['labels'].items():
            if not k.startswith('_'):
                labels.append(":".join([k.strip(), v.strip()]))
        label = str(', '.join(labels))
    elif label.title() == "None":
        label = "None"

    _default_destination = None
    _static_routes = None
    if 'routes' in resp.Response.output:
        if resp.Response.output['routes']:
            itemList = next((item for item in resp.Response.output['routes'] if item["dest"] == "0.0.0.0/0"), None)
            if itemList:
                _default_destination = itemList['via']
                _static_routes = resp.Response.output['routes'][:-1]
            else:
                _default_destination = None
                _static_routes = resp.Response.output['routes']
        elif not resp.Response.output['routes']:
            _default_destination = None
            _static_routes = None

    if isinstance(default_destination, str) and default_destination.title() == "None":
        default_destination = []
        sr = []
    if isinstance(default_destination, str) and default_destination.title() != "None":
        default_destination = [{'destination': "0.0.0.0/0", 'via': default_destination}]
        sr = default_destination
    if default_destination is None and _default_destination is not None:
        default_destination = [{'destination': "0.0.0.0/0", 'via': _default_destination}]
        sr = default_destination
    if default_destination is None and _default_destination is None:
        default_destination = []
        sr = []

    if static_routes is not None and static_routes != []:
        static_routes = re.sub("\s\s+" , " ", static_routes)
        for each_route in static_routes.split(' '):
            if _static_routes:
                itemList = next((item for item in _static_routes if item["dest"] == each_route.split(",")[0]), None)
                if itemList:
                    del _static_routes[
                        ([i for i, _ in enumerate(_static_routes) if _['dest'] == each_route.split(",")[0]][0])]
            if each_route.split(",")[2:]:
                try:
                    import ipaddress
                    ipaddress.ip_network(each_route.split(",")[2:][-1], strict=False)
                    sr.append({"destination": each_route.split(",")[0], "via": each_route.split(",")[1],
                               "allow_from_virtual": each_route.split(",")[2:-1],
                               "local_representation_network":each_route.split(",")[2:][-1]})
                except ValueError:
                    sr.append({"destination": each_route.split(",")[0], "via": each_route.split(",")[1],
                               "allow_from_virtual": each_route.split(",")[2:]})
            else:
                sr.append({"destination": each_route.split(",")[0], "via": each_route.split(",")[1]})
        if _static_routes is not None:
            sr.append(_static_routes)
    elif _static_routes is not None and static_routes is None:
        sr.append(_static_routes)
    elif static_routes is []:
        pass
    del default_destination
    static_routes = list(sr)
    static_routes = json.loads(json.dumps(static_routes).replace('"dest"','"destination"'))
    format_static_routes=list()
    for i in static_routes:
        if isinstance(i, list):
            for j in i:
                format_static_routes.append(j)
        else:
            format_static_routes.append(i)
    static_routes = list(format_static_routes)

    _firewall_selector = list()
    if resp.Response.output['firewall_selector']['match_label']:
        for k, v in resp.Response.output['firewall_selector']['match_label'].items():
            if k.startswith('_') and k.endswith('name'):
                _firewall_selector.append(k)
                _firewall_selector.append(resp.Response.output['firewall_selector']['match_label'][k])
            if k.startswith('_') and k.endswith('hairpin'):
                _firewall_selector.append(k)
                _firewall_selector.append(resp.Response.output['firewall_selector']['match_label'][k])
            if k.startswith('_') and k.endswith('diode'):
                _firewall_selector.append(k)
                _firewall_selector.append(resp.Response.output['firewall_selector']['match_label'][k])
            if bool(re.match('^[a-zA-Z0-9 \-\.\_]+$',k)) and not k.startswith('_'):
                _firewall_selector.append(k)
                _firewall_selector.append(v)

    if firewall_selector is None:
        firewall_selector = _firewall_selector
    elif firewall_selector.title() == "None" or firewall_selector == "remove":
        __firewall_selector = dict(zip(_firewall_selector[::2], _firewall_selector[1::2]))
        for k,v in dict(zip(_firewall_selector[::2], _firewall_selector[1::2])).items():
            if k.startswith('_') and k.endswith('name'):
                del __firewall_selector["_iotium.firewall.name"]
            if bool(re.match('^[a-zA-Z0-9 \-\.\_]+$',k)) and not k.startswith('_'):
                del __firewall_selector[k]
        firewall_selector=[]
        for k, v in __firewall_selector.items():
            firewall_selector.append(k)
            firewall_selector.append(v)
    elif firewall_selector is not None and firewall_selector.title() != "None":
        if bool(re.match('^[a-zA-Z0-9 \-\.\_]+$', firewall_selector)):
            _firewall_selector.append("_iotium.firewall.name")
            _firewall_selector.append(firewall_selector)
        else:
            _firewall_selector.append(firewall_selector.split(':')[0])
            _firewall_selector.append(firewall_selector.split(':')[1])
        firewall_selector = _firewall_selector

    firewall_policy = resp.Response.output['policy']['firewall']['debug'] if firewall_policy is None else firewall_policy

    DISCONNECT_FLAG=False
    if connect_networks is not None:
        if connect_networks != [] and connect_networks[-1] == "DISCONNECT":
            DISCONNECT_FLAG = True
            connect_networks.pop()
    _connect_networks = []

    if 'connected_networks' in resp.Response.output:
        for cn in resp.Response.output['connected_networks']:
            fields=dict()
            if 'node' in cn:
                fields['node_id'] = cn['node']['id']
            if 'network' in cn:
                fields['network_id'] = cn['network']['id']
            if 'representation_network' in cn:
                if 'peer' in cn['representation_network']:
                    fields['peer_representation_network'] = cn['representation_network']['peer']
                if 'local' in cn['representation_network']:
                    fields['local_representation_network'] = cn['representation_network']['local']
            if 'firewall_selector' in cn:
                fields['firewall_selector'] = cn['firewall_selector']
            _connect_networks.append(fields)

    if connect_networks is None:
        connect_networks = _connect_networks
    elif connect_networks:
        for cn in connect_networks:
            #item = next((item for index, item in enumerate(_connect_networks) if item['network_id'] == cn['network_id']), None)
            if _connect_networks:
                temp = [i for i,_ in enumerate(_connect_networks) if _['network_id'] == cn['network_id']]
                if temp:
                    _connect_networks[([i for i, _ in enumerate(_connect_networks) if _['network_id'] == cn['network_id']][0])].update(cn)
                    continue
            _connect_networks.append(cn)

        if DISCONNECT_FLAG:
            for cn in connect_networks:
                temp = [i for i, _ in enumerate(_connect_networks) if _['network_id'] == cn['network_id']]
                index_of_via = [i for i, _ in enumerate(static_routes) if _['via'] == cn['network_id']]
                final_static_route = list()
                for i, j in enumerate(static_routes):
                    if i in index_of_via:
                        continue
                    else:
                        if 'allow_from_virtual' in static_routes[i]:
                            if cn['network_id'] in static_routes[i]['allow_from_virtual']:
                                static_routes[i]['allow_from_virtual'][:] = \
                                    (value for value in static_routes[i]['allow_from_virtual']
                                     if value != cn['network_id'])
                        final_static_route.append(static_routes[i])
                if temp:
                    del _connect_networks[([i for i,_ in enumerate(_connect_networks) if _['network_id'] == cn['network_id']][0])]
                    static_routes = final_static_route
    elif not connect_networks:
        for sr in range(len(static_routes) - 1, -1, -1):
            for sn in _connect_networks:
                if static_routes[sr]['via'] == sn['network_id']:
                    del (static_routes[sr])
                    break
        _connect_networks = []
    else:
        connect_networks = _connect_networks
    
    connect_networks = _connect_networks

    return network(action='edit', network_id=network_id, payload=locals())

def delete(network_id):
    return network(action='delete', network_id=network_id)

def get(network_id=None):
    if network_id is not None:
        return network(action='get_network_id', network_id=network_id)
    else:
        return network(action='get')

def getv2(filters=None):
    return network(action='getv2', filters=filters)

def resetcounter(network_id):
    return network(action='reset_counter', network_id=network_id)