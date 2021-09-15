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

import re


def format_rules(rules):
    newRules = []
    for rule in rules:
        # tuple 1
        if 'source_network' in rule:
            pass
        else:
            rule['source_network'] = {}

        # tuple 2
        if 'destination_network' in rule:
            pass
        else:
            rule['destination_network'] = {}

        # tuple 3
        if 'priority' in rule:
            if not rule['priority']:
                rule['priority'] = 1000
            else:
                pass
        else:
            rule['priority'] = 1000

        # tuple 4
        if 'protocol' in rule:
            if not rule['protocol']:
                rule['protocol'] = 'ANY'
            else:
                pass
        else:
            rule['protocol'] = "ANY"

        if rule['protocol'] == 'ICMP':
            rule['icmp_types'] = ["Echo"]
            rule['destination_port'] = {'start': 1, 'end': 65535}
            rule['source_port'] = {'start': 1, 'end': 65535}
        elif rule['protocol'] == 'ANY':
            rule['destination_port'] = {'start': 1, 'end': 65535}
            rule['source_port'] = {'start': 1, 'end': 65535}
        elif rule['protocol'] == 'HTTPS':
            rule['destination_port'] = {'start': 443, 'end': 443}
            rule['source_port'] = {'start': 1, 'end': 65535}
        elif rule['protocol'] == 'SSH':
            rule['destination_port'] = {'start': 22, 'end': 22}
            rule['source_port'] = {'start': 1, 'end': 65535}
        elif rule['protocol'] == 'TCP':
            if 'destination_port' in rule:
                if not rule['destination_port']:
                    rule['destination_port'] = {'start': 1, 'end': 65535}
                else:
                    pass
            else:
                rule['destination_port'] = {'start': 1, 'end': 65535}
            rule['source_port'] = {'start': 1, 'end': 65535}
        elif rule['protocol'] == 'UDP':
            if 'destination_port' in rule:
                if not rule['destination_port']:
                    rule['destination_port'] = {'start': 1, 'end': 65535}
                else:
                    pass
            else:
                rule['destination_port'] = {'start': 1, 'end': 65535}
            rule['source_port'] = {'start': 1, 'end': 65535}
        else:
            pass

        # tuple 5
        if 'source_ip' in rule:
            if not rule['source_ip']:
                rule['source_ip'] = "0.0.0.0/0"
            else:
                pass
        else:
            rule['source_ip'] = "0.0.0.0/0"

        # tuple 6
        if 'destination_ip' in rule:
            if not rule['destination_ip']:
                rule['destination_ip'] = "0.0.0.0/0"
            else:
                pass
        else:
            rule['destination_ip'] = "0.0.0.0/0"

        if 'action' in rule:
            if not rule['action']:
                rule['action'] = "ALLOW"
            else:
                pass
        else:
            rule['action'] = "DENY"

        newRules.append(rule)
    return newRules


def checkforUriParam(uri):
    return re.findall(r'\{(.*?)\}', uri)


def verifyNodePayload(indict):
    a = ['name', 'profile_id', 'max_headless_time', 'hardware_serial_number', 'create_under',
         'hardware_serial_number_id', 'metadata']
    a = set(a)
    b = set(indict.keys())

    if list(b - a):
        return False

    return True


def get_value_from_nested_dict(obj, chain):
    """
    get the value of the element from nested dictionary
    """
    if type(obj) is list:
        obj = {k: v for x in obj for k, v in list(x.items())}
    _key = chain.pop(0)
    if _key in obj:
        return get_value_from_nested_dict(obj[_key], chain) if chain else obj[_key]


def formattedOutput(resp, method):

    formatted_output = []

    if resp and method=="iNode":

        for ff in resp:
            NodeLabel = []
            if 'labels' in ff['metadata']:
                for k, v in list(ff['metadata']['labels'].items()):
                    if not k.startswith('_'):
                        NodeLabel.append(":".join([k.strip(), v.strip()]))
                if NodeLabel:
                    NodeLabel = str(','.join(NodeLabel))
                else:
                    NodeLabel = "-"
            else:
                NodeLabel = '-'

            InternalIP = []
            ExternalIP = []
            if 'node' in ff['status']:
                if 'addresses' in ff['status']['node']:
                    for addresses_index in range(len(ff['status']['node']['addresses'])):
                        if 'InternalIP' in list(ff['status']['node']['addresses'][addresses_index].values()):
                            InternalIP.append(ff['status']['node']['addresses'][addresses_index]['address'])
                        if 'ExternalIP' in list(ff['status']['node']['addresses'][addresses_index].values()):
                            ExternalIP.append(ff['status']['node']['addresses'][addresses_index]['address'])
                if 'info' in ff['status']['node']:
                    if 'version' in ff['status']['node']['info'] and \
                            'software_version' in ff['status']['node']['info']['version']:
                        Version = ff['status']['node']['info']['version']['software_version']
                    else:
                        Version = 'NA'
                    if 'vendor_oemid' in ff['status']['node']['info']:
                        OEMID = ff['status']['node']['info']['vendor_oemid']
                    else:
                        OEMID = 'NA'
                else:
                    Version = 'NA'
                    OEMID = 'NA'
            else:
                Version = '-'
                OEMID = '-'

            if 'max_headless_time' in ff:
                MaxHeadlessTime = ff['max_headless_time']
            else:
                MaxHeadlessTime = 0

            METRICS_FREQUENCY = str()
            STATUS_MODE = str()
            if 'stat_config' in ff:
                if 'stat_mode' in ff['stat_config']:
                    METRICS_FREQUENCY = ff['stat_config']['stat_mode']
                    if METRICS_FREQUENCY.title() == "Fast":
                        STATUS_MODE = "Disable"
                    elif METRICS_FREQUENCY.title() == "Slow" or METRICS_FREQUENCY.title() == "Off":
                        STATUS_MODE = "Enable"
                    else:
                        STATUS_MODE = ""
                        METRICS_FREQUENCY = ''
            else:
                STATUS_MODE = ""
                METRICS_FREQUENCY = ''

            formatted_output.append(
                {
                    "SerialNumber": ff['hardware_serial_number'],
                    "NodeName": ff['name'],
                    "State": ff['node_state'],
                    "OrgName": ff['organization']['name'],
                    "ProfileName": ff['profile']['name'],
                    "NodeLabel": NodeLabel,
                    "Version": Version,
                    "OEMID": OEMID,
                    "NodeId": ff['id'],
                    "InternalIP": ",".join(InternalIP),
                    "ExternalIP": ",".join(ExternalIP),
                    "StandaloneExpiryTime": MaxHeadlessTime,
                    "DataSavingMode":STATUS_MODE.title(),
                    "MetricsFrequency":METRICS_FREQUENCY.title()
                }
            )

        return formatted_output
    elif resp and method=="Network":
        for networks in resp:

            rn = []
            nxid = []
            s = []
            network_fwg = []
            NetworkLabel=[]

            if 'labels' in networks['metadata']:
                for k, v in list(networks['metadata']['labels'].items()):
                    if not k.startswith('_'):
                        NetworkLabel.append(":".join([k.strip(), v.strip()]))
                if NetworkLabel:
                    NetworkLabel = str(','.join(NetworkLabel))
                else:
                    NetworkLabel = "-"

            else:
                NetworkLabel = '-'

            cidr = '-'
            gateway='-'
            if 'config' in networks:
                if 'network' in networks['config']:
                    if 'cidr' in networks['config']['network']:
                        cidr = networks['config']['network']['cidr']
                    else:
                        cidr = '-'
                    if 'gateway' in networks['config']['network']:
                        gateway = networks['config']['network']['gateway']
                    else:
                        gateway = '-'

            service_addressing = 'AUTO'
            if 'config' in networks:
                if 'network' in networks['config']:
                    if 'service_addressing' in networks['config']['network']:
                        service_addressing = networks['config']['network']['service_addressing']
                    else:
                        service_addressing = '-'


            if service_addressing == 'AUTO':
                service_addressing = 'Dynamic'
            elif service_addressing == 'MANUAL':
                service_addressing = 'Static'
            else:
                service_addressing = '-'


            vlan_id = 0
            if 'config' in networks:
                if 'network' in networks['config']:
                    if 'vlan_id' in networks['config']['network']:
                        vlan_id = networks['config']['network']['vlan_id']
                    else:
                        vlan_id = '-'


            if 'status' in networks:
                if 'connected_networks' in networks['status']:
                    for state in range(len(networks['status']['connected_networks'])):
                        s.append(networks['status']['connected_networks'][state]['state'])
                else:
                    s = '-'
            if 'connected_networks' in networks:
                for cn in range(len(networks['connected_networks'])):
                    if 'node' in networks['connected_networks'][cn]:
                        n = '{}/{}'.format(networks['connected_networks'][cn]['node']['name'],
                                           networks['connected_networks'][cn]['network']['name'])
                        rn.append(n)
                    if 'cluster' in networks['connected_networks'][cn]:
                        n = '{}/{}'.format(networks['connected_networks'][cn]['cluster']['name'],
                                           networks['connected_networks'][cn]['network']['name'])
                        rn.append(n)
                    if 'representation_network' in networks['connected_networks'][cn]:
                        if 'local' in networks['connected_networks'][cn]['representation_network']:
                            nxid.append(networks['connected_networks'][cn]['representation_network']['local'])
                        else:
                            nxid.append('-')
                    else:
                        nxid.append('-')
            else:
                rn = '-'
                nxid.append('-')

            if 'firewall_selector' in networks:
                if 'match_label' in networks['firewall_selector']:
                    applied_fwg = [x for x in list(networks['firewall_selector']['match_label'].keys()) if
                                   x not in ['_iotium.firewall.fwg', '_iotium.firewall.hairpin', '_iotium.fwg.virtual']]
                    if applied_fwg:
                        for fwg in applied_fwg:
                            if fwg.startswith('_'):
                                network_fwg.append(networks['firewall_selector']['match_label'][fwg])
                            else:
                                network_fwg.append(
                                    "{}:{}".format(fwg, networks['firewall_selector']['match_label'][fwg]))
                    else:
                        network_fwg.append('-')

            #if type(rn) is list and len(rn) >= 2:
            #    rn = "{} Networks".format(len(rn))
            #else:
            #    rn = ','.join(rn)

            default_destination="None"
            if 'routes' in networks:
                for index, routes in enumerate(networks['routes']):
                    if 'via' in networks['routes'][index]:
                        default_destination = networks['routes'][index]['via']
                    else:
                        default_destination = 'None'

            node_name = str()
            node_id = str()
            cluster_name = str()
            cluster_id = str()
            if 'node' in networks:
                node_name = networks['node']['name']
                node_id = networks['node']['id']
            if 'cluster' in networks:
                cluster_name = networks['cluster']['name']
                cluster_id = networks['cluster']['id']

            formatted_output.append({"NetworkName": networks['name'],
                                     "NetworkLabel":NetworkLabel,
                                     "NetworkId":networks['id'],
                                     networks['id']:"{}/{}".format(node_name if node_name else cluster_name, networks['name']),
                                     "NodeName": node_name,
                                     "NetworkNodeName": node_name,
                                     "NetworkClusterName": cluster_name,
                                     "NodeId": node_id,
                                     "ClusterId" : cluster_id,
                                     "Organization": networks['organization']['name'],
                                     "RemoteNetwork(s)": ','.join(rn),
                                     "RepresentedAs": ','.join(nxid),
                                     "ServiceAddressingMode": service_addressing,
                                     "CIDR": cidr,
                                     "GatewayIpAddress":gateway,
                                     "VlanId":vlan_id,
                                     "CustomSecurityPolicy": ','.join(network_fwg),
                                     "DefaultDestination": default_destination,
                                     "Status": ','.join(s)})

        for index, op in enumerate(formatted_output):
            if formatted_output[index]['DefaultDestination'].startswith("n-"):
                try:
                    ds= next(d for i, d in enumerate(formatted_output) if formatted_output[index]['DefaultDestination'] in d)
                    _ds="{}/{}".format(ds['NodeName'], ds['NetworkName'])
                    formatted_output[index]['DefaultDestination'] = _ds
                except Exception:
                    formatted_output[index]['DefaultDestination'] = "NOT LOADED"
        return formatted_output
    elif resp and method=="Org":
        for org in resp:
            op = dict()
            if 'billing_name' not in org:
                op['BillingName'] = '-'
            else:
                op['BillingName'] = org['billing_name']
            op['Organization']= org['name']
            op['TotalNode'] = org['node_count']
            op['TotalUser'] = org['user_count']
            op['TotalSecret'] = org['secret_volume_count']

            if 'headless_mode' in org['policy']:
                if 'enable' in org['policy']['headless_mode']:
                    if bool(org['policy']['headless_mode']['enable']):
                        op['Standalone'] = "Enabled"
                    else:
                        op['Standalone'] = "Disabled"
            else:
                op['Standalone'] = "-"

            if 'two_factor' in org['policy']:
                if 'enable' in org['policy']['two_factor']:
                    if bool(org['policy']['two_factor']['enable']):
                        op['2FA'] = "Enabled"
                    else:
                        op['2FA'] = "Disabled"
            else:
                op['2FA'] = "-"

            if 'vlan_support' in org['policy']:
                if 'enable' in org['policy']['vlan_support']:
                    if bool(org['policy']['vlan_support']['enable']):
                        op['VLAN Support'] = "Enabled"
                    else:
                        op['VLAN Support'] = "Disabled"
            else:
                op['VLAN Support'] = "-"

            formatted_output.append(op)
        return formatted_output
    elif resp and method=="Pki":
        for result in resp:
            op = dict()
            op.update({'SerialNumber': result['hardware_serial_number'],
                       'not_after': result['not_after'],
                       'not_before': result['not_before'],
                       'Organization': result['organization']['name'],
                       'NodeLabel': '',
                       'StandaloneExpiryTime': '-',
                       'DataSavingMode':'',
                       'MetricsFrequency':'',
                       'NodeName': '-'})
            if 'node' in result:
                op['NodeName'] = result['node']['name']
            if 'legacy_serial_number' in result:
                op['SerialNumber'] = result['legacy_serial_number']
            formatted_output.append(op)
        return formatted_output
    elif resp and method=="Secret":
        for result in resp:
            op = dict()
            op.update({'SecretName': result['name'],
                       'Organization': result['organization']['name'],
                       'AssignedServices': '-'
                       })
            if 'services' in result and result['services']:
                name = []
                for s in range(len(result['services'])):
                    name.append(result['services'][s]['name'])
                op['AssignedServices'] = ','.join(name)
            formatted_output.append(op)
        return formatted_output
    elif resp and method=="Service":
        from iotiumlib import helper, network, node
        node_details_op = node.getv2().Response.output
        dict_node_op = dict()
        for i in node_details_op:
            dict_node_op.update({i['name']: i})
        for result in resp:
            op = dict()
            node_name = str()
            cluster_name = str()
            service_status = str()
            if 'status' in result:
                if 'status' in result['status']:
                    service_status = result['status']['status']                    
            if 'node' in result:
                node_name = result['node']['name']
            if 'cluster' in result:
                cluster_name = result['cluster']['name']
                if 'kind' in result['spec'] and (result['spec']['kind'] == 'REPLICA' or result['spec']['kind'] == 'DAEMON'):
                    service_status = '-'

            op.update({'ServiceName': result['name'],
                       'NodeName': node_name,
                       'ClusterName' : cluster_name,
                       'ServiceStatus': service_status,
                       'Organization': result['organization']['name'],
                       'ServiceIp': '-',
                       'TotalContainers': '-',
                       'Message':'-'
                       })
            if 'service_ip' in result['status']:
                for ip in range(len(result['status']['service_ip'])):
                    op['ServiceIp'] = result['status']['service_ip'][ip]['ip_address']
                    op['ServiceMacAddress'] = result['status']['service_ip'][ip]['mac_address']
                    #op['NetworkName']=helper.get_resource_name_by_id(network, result['status']['service_ip'][ip]['network_id'])
            if 'running' in result['status']:
                op['TotalContainers'] = result['status']['running']
            if 'message' in result['status']:
                op['Message'] = result['status']['message']
            if 'container_status' in result['status']:
                container_image = list()
                for each_containter_status in range(len(result['status']['container_status'])):
                    container_image.append(result['status']['container_status'][each_containter_status]['image'])
                op['ContainerImage'] = ','.join(container_image)
            if 'spec' in result:
                if 'dns_policy' in result['spec']:
                    op['DnsPolicy'] = result['spec']['dns_policy']
                if 'dns' in result['spec']:
                    op['DnsServerIpAddress'] = ','.join(result['spec']['dns'])
                else:
                    if 'dns' in result['status']:
                        op['DnsServerIpAddress'] = ','.join(result['status']['dns']['nameserver'])
                    if False:
                        if result['node']['name'] in dict_node_op:
                            node_get_op = dict_node_op[result['node']['name']]
                            if 'node' in node_get_op['status']:
                                if 'dns' in node_get_op['status']['node']:
                                    op['DnsServerIpAddress'] = ','.join(node_get_op['status']['node']['dns']['nameserver'])
            formatted_output.append(op)
        return formatted_output
    elif resp and method=="FWG":
        default_fwg = ['hairpin-allow', 'ingress-only', 'egress-only', 'tandefault', 'virtual-ingress', 'default']
        for result in resp:
            op = dict()
            FwgLabel = list()
            if result['name'] not in default_fwg:
                op.update({'FwgName' : result['name'],
                           'FwgLabel': '-'
                })
                if 'labels' in result['metadata']:
                    for k, v in list(result['metadata']['labels'].items()):
                        if not k.startswith('_'):
                            FwgLabel.append(":".join([k.strip(), v.strip()]))
                    if FwgLabel:
                        FwgLabel = str(','.join(FwgLabel))
                    else:
                        FwgLabel = "-"
                else:
                    FwgLabel = '-'
                op['FwgLabel'] = FwgLabel
                formatted_output.append(op)
        return formatted_output
    elif resp and method=="Notifications":
        for result in resp:
            op = dict()
            op.update({'EventType': result['type'],
                       'Status': result['status'],
                       'Organization': result['organization']['name'],
                       'NodeName': result['node']['name']
                       })
            formatted_output.append(op)
        return formatted_output
    elif resp and method=="User":
        for users in resp:
            op = dict()
            op.update(
                {
                    "UserName":users['username'],
                    "FullName":users['name'],
                    "EmailAddress":users['email'],
                    "EmailVerified":users['email_verified'],
                    "Role":""
                }
            )
            role_name = ','.join(str(x['name']) for x in users['roles'])
            op.update({"Role":role_name})
            formatted_output.append(op)
        return formatted_output
    return resp
