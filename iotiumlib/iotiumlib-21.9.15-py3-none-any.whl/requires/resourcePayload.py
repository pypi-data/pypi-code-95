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

from iotiumlib.requires.Exceptions import *
from iotiumlib.requires.utils import *


class resourcePaylod(object):

    class Metadata(object):

        def __init__(self, payload):

            metadataObj = resourcePaylod.Metadata.Label()

            if 'label' in payload and payload['label'] is not None and \
                    payload['label'] and payload['label'].title() != "None":
                setattr(metadataObj, 'metadata', payload['label'])
            self.metadata = getattr(metadataObj, 'metadata', {"labels": {}})

        class Label(object):
            def __init__(self):
                self._metadata={"labels": {}}

            @property
            def metadata(self):
                return self._metadata

            @metadata.setter
            def metadata(self, metadata):
                metadata = [i for i in metadata.split(',') if i]
                for l in metadata:
                    b = dict([l.strip().split(':')])
                    self._metadata['labels'].update(b)

    class Organisation(object):

        def __init__(self, payload):

            orgId_Obj = resourcePaylod.Organisation.orgId()
            orgName_Obj = resourcePaylod.Organisation.orgName()
            orgBillingName_Obj = resourcePaylod.Organisation.orgBillingName()
            orgBillingEmail_Obj = resourcePaylod.Organisation.orgBillingEmail()
            headlessMode_Obj = resourcePaylod.Organisation.headlessMode()
            TwoFA_Obj = resourcePaylod.Organisation.TwoFA()
            Vlan_Obj = resourcePaylod.Organisation.Vlan()


            if 'org_id' in payload:
                setattr(orgId_Obj, 'org_id', payload['org_id'])
            else:
                setattr(orgId_Obj, 'org_id', "")
            self.create_under = getattr(orgId_Obj, 'org_id')

            if 'org_name' in payload:
                setattr(orgName_Obj, 'org_name', payload['org_name'])
            else:
                setattr(orgName_Obj, 'org_name', "")
            self.name = getattr(orgName_Obj, 'org_name')

            if 'billing_name' in payload:
                setattr(orgBillingName_Obj, 'billing_name', payload['billing_name'])
            else:
                setattr(orgBillingName_Obj, 'billing_name', "")
            self.billing_name = getattr(orgBillingName_Obj, 'billing_name')

            if 'billing_email' in payload:
                setattr(orgBillingEmail_Obj, 'billing_email', payload['billing_email'])
            else:
                setattr(orgBillingEmail_Obj, 'billing_email', "")
            self.billing_email = getattr(orgBillingEmail_Obj, 'billing_email')

            if 'headless_mode' in payload:
                setattr(headlessMode_Obj, 'headless_mode', payload['headless_mode'])
            else:
                setattr(headlessMode_Obj, 'headless_mode', False)
            self.headless_mode = getattr(headlessMode_Obj, 'headless_mode')

            if 'two_factor' in payload:
                setattr(TwoFA_Obj, 'two_factor', payload['two_factor'])
            else:
                setattr(TwoFA_Obj, 'two_factor', False)
            self.two_factor_authenticate = getattr(TwoFA_Obj, 'two_factor')

            if 'vlan_support' in payload:
                setattr(Vlan_Obj, 'vlan_support', payload['vlan_support'])
            else:
                setattr(Vlan_Obj, 'vlan_support', False)
            self.vlan_support = getattr(Vlan_Obj, 'vlan_support')


        class orgId(object):
            def __init__(self):
                self._orgId = str()

            @property
            def org_id(self):
                return self._orgId

            @org_id.setter
            def org_id(self, org_id):
                self._orgId = org_id

        class orgName(object):
            def __init__(self):
                self._org_name = str()

            @property
            def org_name(self):
                return self._org_name

            @org_name.setter
            def org_name(self, org_name):
                self._org_name = org_name

        class orgBillingName(object):
            def __init__(self):
                self._billing_name = str()

            @property
            def billing_name(self):
                return self._billing_name

            @billing_name.setter
            def billing_name(self, billing_name):
                self._billing_name = billing_name

        class orgBillingEmail(object):
            def __init__(self):
                self._billing_email = str()

            @property
            def billing_email(self):
                return self._billing_email

            @billing_email.setter
            def billing_email(self, billing_email):
                self._billing_email = billing_email

        class headlessMode(object):
            def __init__(self):
                self._headless_mode = bool()

            @property
            def headless_mode(self):
                return self._headless_mode

            @headless_mode.setter
            def headless_mode(self, mode):
                self._headless_mode = mode

        class TwoFA(object):
            def __init__(self):
                self._2fa = bool()

            @property
            def two_factor(self):
                return self._2fa

            @two_factor.setter
            def two_factor(self, mode):
                self._2fa = mode

        class Vlan(object):
            def __init__(self):
                self._vlan_support = bool()

            @property
            def vlan_support(self):
                return self._vlan_support

            @vlan_support.setter
            def vlan_support(self, flag):
                self._vlan_support = flag

    class iNode(object):

        def __init__(self, payload):

            nodeName_Obj = resourcePaylod.iNode.nodeName()
            profileId_Obj = resourcePaylod.iNode.profileId()
            pkiId_Obj = resourcePaylod.iNode.pkiId()
            orgIdObj = resourcePaylod.Organisation.orgId()
            standaloneTime_Obj = resourcePaylod.iNode.standaloneTime()
            labelObj = resourcePaylod.Metadata.Label()
            dataSavingModeObj = resourcePaylod.iNode.dataSavingMode()
            sshkeyObj = resourcePaylod.iNode.sshKey()
            containerTimeZoneObj = resourcePaylod.iNode.containerTimeZone

            if 'inode_name' in payload and payload['inode_name']:
                setattr(nodeName_Obj, 'name', payload['inode_name'])
            else:
                setattr(nodeName_Obj, 'name', "")
            self.name = getattr(nodeName_Obj, 'name')

            if 'profile_id' in payload and payload['profile_id']:
                setattr(profileId_Obj, 'profile_id', payload['profile_id'])
            else:
                setattr(profileId_Obj, 'profile_id', "")
            self.profile_id = getattr(profileId_Obj, 'profile_id')

            if 'serial_number' in payload and payload['serial_number']:
                setattr(pkiId_Obj, 'hardware_serial_number', payload['serial_number'])
                self.hardware_serial_number = getattr(pkiId_Obj, 'hardware_serial_number')

            if 'org_id' in payload and payload['org_id']:
                setattr(orgIdObj, 'org_id', payload['org_id'])
            self.create_under = getattr(orgIdObj, 'org_id')

            if 'standalone_expires' in payload and payload['standalone_expires'] is not None and \
                    isinstance(payload['standalone_expires'], int):
                setattr(standaloneTime_Obj, 'max_headless_time', payload['standalone_expires'])
            else:
                setattr(standaloneTime_Obj, 'max_headless_time', 0)
            self.max_headless_time = getattr(standaloneTime_Obj, 'max_headless_time')

            if 'label' in payload and payload["label"] is not None and \
                            payload["label"].title() != "None" and payload["label"]:
                setattr(labelObj, "metadata", payload["label"])
            self.metadata = getattr(labelObj, 'metadata', {"labels": {}})

            if 'data_saving_mode' in payload and payload["data_saving_mode"] is not None and payload["data_saving_mode"]:
                setattr(dataSavingModeObj, 'data_saving_mode', payload['data_saving_mode'])
            else:
                setattr(dataSavingModeObj, 'data_saving_mode', "Fast")
            self.stat_mode = getattr(dataSavingModeObj, 'data_saving_mode').upper()

            if 'ssh_keys' in payload and payload["ssh_keys"] is not None and payload["ssh_keys"]:
                setattr(sshkeyObj, 'ssh_keys', payload['ssh_keys'])
                self.ssh_keys = getattr(sshkeyObj, 'ssh_keys')

            if 'container_timezone' in payload and payload['container_timezone']:
                setattr(containerTimeZoneObj, 'container_timezone', payload['container_timezone'])
                self.container_timezone = getattr(containerTimeZoneObj, 'container_timezone')

        class nodeName(object):
            def __init__(self):
                self._nodeName = str()

            @property
            def name(self):
                return self._nodeName

            @name.setter
            def name(self, name):
                self._nodeName = name

        class profileId(object):
            def __init__(self):
                self._profileId = str()

            @property
            def profile_id(self):
                return self._profileId

            @profile_id.setter
            def profile_id(self, profile_id):
                self._profileId = profile_id

        class pkiId(object):
            def __init__(self):
                self._pkiId = str()

            @property
            def hardware_serial_number(self):
                return self._pkiId

            @hardware_serial_number.setter
            def hardware_serial_number(self, hardware_serial_number):
                self._pkiId = hardware_serial_number

        class orgId(object):
            def __init__(self):
                self._orgId = str()

            @property
            def create_under(self):
                return self._orgId

            @create_under.setter
            def create_under(self, create_under):
                self._orgId = create_under

        class standaloneTime(object):
            def __init__(self):
                self._standaloneTime = 0

            @property
            def max_headless_time(self):
                return self._standaloneTime

            @max_headless_time.setter
            def max_headless_time(self, max_headless_time):
                self._standaloneTime = max_headless_time

        class dataSavingMode(object):
            def __init__(self):
                self._data_saving_mode = "Fast"

            @property
            def data_saving_mode(self):
                return self._data_saving_mode

            @data_saving_mode.setter
            def data_saving_mode(self, mode):
                self._data_saving_mode = mode

        class sshKey(object):
            def __init__(self):
                self._sshkey = list()
            
            @property
            def ssh_keys(self):
                return self._sshkey

            @ssh_keys.setter
            def ssh_keys(self, key):
                self._sshkey.append(key)

        class containerTimeZone(object):
            def __init__(self):
                self._value = str()

            @property
            def container_timezone(self):
                return self._value

            @container_timezone.setter
            def container_timezone(self, value):
                self._value = value


    class Network(object):
        def __init__(self, payload):

            if payload == {}:
                return

            self.interface = "eth1"
            networkTypeObj = resourcePaylod.Network.NetworkType()
            if 'network_addressing' in payload and payload['network_addressing']:
                setattr(networkTypeObj, 'network_type', payload['network_addressing'])
                self.network_type = getattr(networkTypeObj, 'network_type')

            interfaceIpObj = resourcePaylod.Network.InterfaceIp()
            if 'interface_ip' in payload and payload['interface_ip']:
                setattr(interfaceIpObj, 'interface_ip', payload['interface_ip'])
                self.tan_interface_ip = getattr(interfaceIpObj, 'interface_ip')

            if 'node_id' in payload and payload['node_id']:
                self.node_id = payload['node_id']

            if 'cluster_id' in payload and payload['cluster_id']:
                self.cluster_id = payload['cluster_id']

            networkNameObj = resourcePaylod.Network.NetworkName()
            if 'network_name' in payload and payload['network_name'] is not None and payload['network_name']:
                setattr(networkNameObj, 'name', payload['network_name'])
                self.name = getattr(networkNameObj, 'name')

            if payload['network_name'] != "WAN Network":
                cidrObj = resourcePaylod.Network.Cidr()
                reservedObj = resourcePaylod.Network.Reserved()
                routesObj = resourcePaylod.Network.Routes()
                vlanObj = resourcePaylod.Network.VlanId()
                cnnObj = resourcePaylod.Network.ConnectNetworks()
                serviceAddressingObj = resourcePaylod.Network.ServiceAddressing()
                gatewayObj = resourcePaylod.Network.Gateway()

                if 'cidr' in payload and payload['cidr']:
                    setattr(cidrObj, 'cidr', payload['cidr'])
                    self.cidr = getattr(cidrObj, 'cidr')

                if 'start_ip' in payload and payload['start_ip'] is not None and payload['start_ip']:
                    setattr(reservedObj, 'start', payload['start_ip'])
                else:
                    setattr(reservedObj, 'start', payload['start_ip'])
                #self.reserved = getattr(reservedObj, 'start')

                if 'end_ip' in payload and payload['end_ip'] is not None and payload['end_ip']:
                    setattr(reservedObj, 'end', payload['end_ip'])
                else:
                    setattr(reservedObj, 'end', payload['start_ip'])
                self.reserved = getattr(reservedObj, 'end', getattr(reservedObj, 'start'))

                if 'gateway_ip' in payload and payload['gateway_ip'] is not None and \
                                payload['gateway_ip'].title() != "None":
                    setattr(gatewayObj, 'gateway', payload['gateway_ip'])
                else:
                    setattr(gatewayObj, 'gateway', payload['start_ip'])
                self.gateway = getattr(gatewayObj, 'gateway', getattr(reservedObj, 'start'))

                if 'default_destination' in payload and payload['default_destination'] is not None and \
                        payload['default_destination']:
                    setattr(routesObj, 'routes', payload['default_destination'])
                self.routes = getattr(routesObj, 'routes', [])

                if 'static_routes' in payload and payload['static_routes'] is not None:
                    if isinstance(payload['static_routes'], list):
                        for each_route in payload['static_routes']:
                            setattr(routesObj, 'routes', each_route)
                self.routes = (getattr(routesObj, 'routes', []))

                if 'vlan_id' in payload and payload['vlan_id'] != 0:
                    setattr(vlanObj, 'vlan_id', payload['vlan_id'])
                self.vlan_id = getattr(vlanObj, 'vlan_id', 0)

                if 'connect_networks' in payload and payload['connect_networks']:
                    for cnn in payload['connect_networks']:
                        setattr(cnnObj, 'connect_networks', cnn)
                self.connect_networks = getattr(cnnObj, 'connect_networks', [])

                if 'service_addressing' in payload and payload['service_addressing']:
                    setattr(serviceAddressingObj, 'service_addressing', payload['service_addressing'])
                self.service_addressing = getattr(serviceAddressingObj, 'service_addressing', "AUTO")

            metadataObj = resourcePaylod.Metadata.Label()
            firewallObj=resourcePaylod.Network.FirewallSelector()
            policyObj = resourcePaylod.Network.Policy()

            if 'label' in payload and payload['label'] is not None and payload['label'] and \
                            payload['label'].title() != "None":
                setattr(metadataObj, 'metadata', payload['label'])
            self.metadata = getattr(metadataObj, 'metadata', {"labels": {}})

            if 'firewall_selector' in payload and payload['firewall_selector'] is not None and payload['firewall_selector']:
                setattr(firewallObj, 'firewall_selector', payload['firewall_selector'])
                self.firewall_selector = getattr(firewallObj, 'firewall_selector')
            else:
                self.firewall_selector = None


            if 'firewall_policy' in payload and payload['firewall_policy'] is not None and payload['firewall_policy']:
                setattr(policyObj, 'firewall_policy', payload['firewall_policy'])
            self.policy = getattr(policyObj, 'firewall_policy', {"firewall": {"debug": False}})

        class InterfaceIp(object):
            def __init__(self):
                self._ip = str()

            @property
            def interface_ip(self):
                return self._ip

            @interface_ip.setter
            def interface_ip(self, ip):
                self._ip = ip

        class NetworkType(object):
            def __init__(self):
                self._type = "STATIC"

            @property
            def network_type(self):
                return self._type

            @network_type.setter
            def network_type(self, type):
                self._type = type.upper()

        class Cidr(object):
            def __init__(self):
                self._cidr = str()
            @property
            def cidr(self):
                return self._cidr

            @cidr.setter
            def cidr(self, cidr):
                self._cidr = cidr

        class FirewallSelector(object):
            def __init__(self):
                self._firewall_selector = {"match_label": {}}

            @property
            def firewall_selector(self):
                return self._firewall_selector

            @firewall_selector.setter
            def firewall_selector(self, firewall_selector):
                if isinstance(firewall_selector, str):
                    if bool(re.match('^[a-zA-Z0-9 \-\.\_]+$',firewall_selector)):
                        self._firewall_selector = {"match_label": {"_iotium.firewall.name": firewall_selector}}
                    else:
                        self._firewall_selector = {"match_label": {firewall_selector.split(':')[0]: firewall_selector.split(':')[1]}}
                if isinstance(firewall_selector, list):
                    self._firewall_selector = {"match_label": dict(zip(firewall_selector[::2], firewall_selector[1::2]))}

        class NetworkName(object):
            def __init__(self):
                self._name = str()

            @property
            def name(self):
                return self._name

            @name.setter
            def name(self, name):
                self._name = name

        class Policy(object):
            def __init__(self):
                self._policy = {"firewall": {"debug": bool()}}

            @property
            def firewall_policy(self):
                return self._policy

            @firewall_policy.setter
            def firewall_policy(self, firewall_policy):
                self._policy = {"firewall": {"debug": firewall_policy}}

        class Gateway(object):
            def __init__(self):
                self._gateway = str()
                
            @property
            def gateway(self):
                return self._gateway
            
            @gateway.setter
            def gateway(self, value):
                self._gateway = value
                
        class Reserved(object):
            def __init__(self):
                self._reserved = {"start": str(), "end":str()}

            @property
            def start(self):
                return self._reserved

            @start.setter
            def start(self, start):
                self._reserved["start"]= start

            @property
            def end(self):
                return self._reserved

            @end.setter
            def end(self, end):
                self._reserved["end"] = end

        class Routes(object):
            def __init__(self):
                self._routes = list(dict())

            @property
            def routes(self):
                return self._routes

            @routes.setter
            def routes(self, routes):
                self._routes.append(routes)

        class VlanId(object):
            def __init__(self):
                self._vlan = int()

            @property
            def vlan_id(self):
                return self._vlan

            @vlan_id.setter
            def vlan_id(self, vlan):
                self._vlan = vlan

        class ConnectNetworks(object):
            def __init__(self):
                self._connect_networks = list(dict())

            @property
            def connect_networks(self):
                return self._connect_networks

            @connect_networks.setter
            def connect_networks(self, ld):
                self._connect_networks.append(ld)

        class ServiceAddressing(object):
            def __init__(self):
                self._service_addressing = "AUTO"

            @property
            def service_addressing(self):
                return self._service_addressing

            @service_addressing.setter
            def service_addressing(self, mode):
                self._service_addressing = mode

    class FWG(object):

        def __init__(self, payload):

            if payload == {}:
                return

            nameObj = resourcePaylod.FWG.Name()
            orgIdObj = resourcePaylod.Organisation.orgId()
            labelObj = resourcePaylod.Metadata.Label()

            if 'name' in payload:
                setattr(nameObj, 'name', payload['name'])
            self.name = getattr(nameObj, 'name', "")

            setattr(orgIdObj, "org_id", payload["org_id"])
            self.create_under = getattr(orgIdObj, 'org_id', "")

            if payload["label"] is not None and payload["label"].title() != "None":
                setattr(labelObj, "metadata", payload["label"])
            #self.metadata = getattr(labelObj, 'metadata', "")
            self.metadata = getattr(labelObj, 'metadata', {"labels": {}})

            self.rules = []

            for r in payload['rules']['rules']:

                fromNetObj = resourcePaylod.FWG.FromNetwork()
                toNetObj = resourcePaylod.FWG.ToNetwork()
                prioObj = resourcePaylod.FWG.Priority()
                protoObj = resourcePaylod.FWG.Protocol()
                sCidrObj = resourcePaylod.FWG.SourceCidr()
                dCidrObj = resourcePaylod.FWG.DestinationCidr()
                actionObj = resourcePaylod.FWG.Action()

                if 'source_cidr' in r:
                    setattr(sCidrObj, 'source_cidr', r['source_cidr'])
                source_cidr = getattr(sCidrObj, 'source_cidr', "")

                if 'destination_cidr' in r:
                    setattr(dCidrObj, 'destination_cidr', r['destination_cidr'])
                destination_cidr = getattr(dCidrObj, 'destination_cidr', "")

                if 'action' in r:
                    setattr(actionObj, 'action', r['action'])
                action = getattr(actionObj, 'action', "")

                if 'priority' in r:
                    setattr(prioObj, 'priority', r['priority'])
                priority = getattr(prioObj, 'priority', "")

                if 'from_network' in r:
                    setattr(fromNetObj, 'from_network', r['from_network'])
                source_network = getattr(fromNetObj, 'from_network', "")

                if 'to_network' in r:
                    setattr(toNetObj, 'to_network', r['to_network'])
                to_network = getattr(toNetObj, 'to_network', "")

                if 'protocol' in r:
                    setattr(protoObj, 'protocol', r['protocol'])
                else:
                    setattr(protoObj, 'protocol', 'ANY')
                protocol = getattr(protoObj, 'protocol', "ANY")

                if 'source_port' in payload and r['source_port'] is not None:
                    protoObj.sp.start = r['source_port']
                    protoObj.sp.end = r['source_port']
                if 'destination_port' in r and r['destination_port'] is not None:
                    protoObj.sp.start = r['destination_port']
                    protoObj.dp.start = r['destination_port']


                self.rules.append(
                    {
                        "source_network": source_network,
                        "destination_network": to_network,
                        "protocol":protocol,
                        "source_port":getattr(protoObj.sp, 'start'),
                        "destination_port": getattr(protoObj.dp, 'end'),
                        "priority": priority,
                        "destination_ip":destination_cidr,
                        "source_ip":source_cidr,
                        "action":action
                    }
                )

        class Name(object):
            def __init__(self):
                self._name = str()

            @property
            def name(self):
                return self._name

            @name.setter
            def name(self, name):
                self._name = name


        class FromNetwork(object):
            def __init__(self):
                self._from_network = dict()

            @property
            def from_network(self):
                return self._from_network

            @from_network.setter
            def from_network(self, from_network):
                check_for_type = from_network.split('=')
                if len(check_for_type) == 1:
                    self._from_network = {}
                    #raise ioTiumArgValueError("ArgValue should be in from_network='id=n-'")
                else:
                    if check_for_type[0] == "id":
                        self._from_network = {"_iotium.network.id":check_for_type[1]}
                    elif check_for_type[0] == "type":
                        self._from_network = {"_iotium.network.type":check_for_type[1]}
                    elif check_for_type[0] == "name":
                        self._from_network = {"_iotium.network.name":check_for_type[1]}
                    elif check_for_type[0] == "label":
                        self._from_network = {check_for_type[1].split(':')[0]: check_for_type[1].split(':')[1]}
                    else:
                        raise ArgValueError

        class ToNetwork(object):
            def __init__(self):
                self._to_network = dict()

            @property
            def to_network(self):
                return self._to_network

            @to_network.setter
            def to_network(self, to_network):
                check_for_type = to_network.split('=')
                if len(check_for_type) == 1:
                    self._to_network = {}
                    #raise ioTiumArgValueError("ArgValue should be in from_network='id=n-'")
                else:
                    if check_for_type[0] == "id":
                        self._to_network = {"_iotium.network.id":check_for_type[1]}
                    elif check_for_type[0] == "type":
                        self._to_network = {"_iotium.network.type":check_for_type[1]}
                    elif check_for_type[0] == "name":
                        self._to_network = {"_iotium.network.name":check_for_type[1]}
                    elif check_for_type[0] == "label":
                        self._to_network = {check_for_type[1].split(':')[0]: check_for_type[1].split(':')[1]}
                    else:
                        raise ArgValueError

        class Priority(object):
            def __init__(self):
                self._priority = 1000

            @property
            def priority(self):
                return self._priority

            @priority.setter
            def priority(self, prio):
                self._priority = prio

        class Protocol(object):
            def __init__(self):
                self._protocol = "ANY"
                self.sp = self.Port()
                self.dp = self.Port()
                self.type=self.Port()

            class Port:
                def __init__(self):
                    self._port = dict()

                @property
                def start(self):
                    return self._port

                @start.setter
                def start(self, start):
                    self._port.update({"start": start})

                @property
                def end(self):
                    return self._port

                @end.setter
                def end(self, end):
                    self._port.update({"end": end})

                @property
                def type(self):
                    return self._port

                @type.setter
                def type(self, type):
                    self._port.update({"icmp_types": type})

            @property
            def protocol(self):
                return self._protocol

            @protocol.setter
            def protocol(self, protocol):
                self._protocol = protocol
                if protocol == "ANY":
                    self.sp.start = 1
                    self.sp.end = 65535
                    self.dp.start = 1
                    self.dp.end = 65535
                elif protocol == "HTTPS":
                    self._protocol = "TCP"
                    self.sp.start = 1
                    self.sp.end = 65535
                    self.dp.start= 443
                    self.dp.end=443
                elif protocol == "SSH":
                    self._protocol = "TCP"
                    self.sp.start = 1
                    self.sp.end = 65535
                    self.dp.start= 22
                    self.dp.end=22
                elif protocol == "ICMP":
                    self.sp.start = 1
                    self.sp.end = 65535
                    self.dp.start= 22
                    self.dp.end=22
                    self.type.type="Echo"
                elif protocol == "TCP":
                    self.sp.start = 1
                    self.sp.end = 65535
                    self.dp.start= 1
                    self.dp.end=65535
                elif protocol == "UDP":
                    self.sp.start = 1
                    self.sp.end = 65535
                    self.dp.start= 1
                    self.dp.end=65535

        class SourceCidr(object):
            def __init__(self):
                self.sIp="0.0.0.0/0"

            @property
            def source_cidr(self):
                return self.sIp

            @source_cidr.setter
            def source_cidr(self, sip):
                self.sIp = sip

        class DestinationCidr(object):
            def __init__(self):
                self.dIp = "0.0.0.0/0"

            @property
            def destination_cidr(self):
                return self.dIp

            @destination_cidr.setter
            def destination_cidr(self, dip):
                self.dIp = dip

        class Action(object):
            def __init__(self):
                self._action = "DENY"

            @property
            def action(self):
                return self._action

            @action.setter
            def action(self, action):
                self._action = action

    class Secret(object):
        def __init__(self, payload):

            if payload == {}:
                return

            nameObj = resourcePaylod.Secret.Name()
            typeObj = resourcePaylod.Secret.Type()
            dataObj = resourcePaylod.Secret.Data()

            if 'name' in payload:
                setattr(nameObj, 'name', payload['name'])
            self.name = getattr(nameObj, 'name', "")

            if 'type' in payload:
                setattr(typeObj, 'type', payload['type'])
            self.type = getattr(typeObj, 'type', "Opaque")

            if self.type != "Opaque":
                self.labels = {"type": "dockerconfig"}

            self.data = dict()
            if 'filename' in payload and payload['filename'] and isinstance(payload['filename'], list):
                for fn in payload['filename']:
                    setattr(dataObj, 'filename', fn)
                self.data = getattr(dataObj, 'filename')
            elif isinstance(payload['filename'], dict):
                for k,v in payload['filename'].items():
                    self.data.update({k:v})




        class Name(object):
            def __init__(self):
                self._name = str()

            @property
            def name(self):
                return self._name

            @name.setter
            def name(self, name):
                self._name = name

        class Type(object):
            def __init__(self):
                self._type = "Opaque"

            @property
            def type(self):
                return self._type

            @type.setter
            def type(self, type):
                self._type = type

        class Data(object):
            def __init__(self):
                self._data = dict()

            @property
            def filename(self):
                return self._data

            @filename.setter
            def filename(self, fn):
                import base64, os
                self._data.update({os.path.basename(fn):base64.b64encode(open(fn, 'rb').read()).decode('ascii')})

    class Service(object):
        def __init__(self, payload):
            pass
        pass

    class Orch(object):
        def __init__(self, payload):
            global usernameObj; usernameObj = resourcePaylod.Orch.Username()
            passwordObj = resourcePaylod.Orch.Password()
            otpObj = resourcePaylod.Orch.OTP()

            if 'username' in payload:
                setattr(usernameObj, 'username', payload['username'])
            else:
                setattr(usernameObj, 'username', "")
            self.username = getattr(usernameObj, 'username')

            if 'password' in payload:
                setattr(passwordObj, 'password', payload['password'])
            else:
                setattr(passwordObj, 'password', "")
            self.password = getattr(passwordObj, 'password')

            if 'otp' in payload and payload['otp'] is not None:
                setattr(otpObj, 'otp', payload['otp'])
                self.otp = getattr(otpObj, 'otp')

        class OTP(object):
            def __init__(self):
                self._otp = str()

            @property
            def otp(self):
                return self._otp

            @otp.setter
            def otp(self, value):
                self._otp = value

        class Username(object):
            def __init__(self):
                self._username = str()

            @property
            def username(self):
                return self._username

            @username.setter
            def username(self, user):
                self._username = user

        class Password(object):
            def __init__(self):
                self._password = str()

            @property
            def password(self):
                return self._password

            @password.setter
            def password(self, pwd):
                self._password = pwd

    class IMAGE(object):

        def __init__(self, payload):

            if payload == {}:
                return

    class User(object):
        def __init__(self, payload):

            if payload == {}:
                return

            nameObj = resourcePaylod.User.Name()
            passwordObj = resourcePaylod.User.Password()
            emailObj = resourcePaylod.User.Email()
            roleObj = resourcePaylod.User.Roles()
            orgId_Obj = resourcePaylod.Organisation.orgId()

            if 'name' in payload and payload['name'] is not None:
                setattr(nameObj, "name", payload['name'])
            self.name = getattr(nameObj, "name", None)

            if 'password' in payload and payload['password'] is not None:
                setattr(passwordObj, "password", payload['password'])
            self.password = getattr(passwordObj, "password", None)

            if 'email' in payload and payload['email'] is not None:
                setattr(emailObj, "email", payload['email'])
            self.email = getattr(emailObj, "email", None)

            if 'role_id' in payload and payload['role_id'] is not None:
                setattr(roleObj, "roles", payload['role_id'])
            self.roles = getattr(roleObj, "roles", [])

            if 'org_id' in payload and payload['org_id'] is not None:
                setattr(orgId_Obj, 'org_id', payload['org_id'])
                self.create_under = getattr(orgId_Obj, 'org_id', None)

        class Name(object):
            def __init__(self):
                self._name = str()

            @property
            def name(self):
                return self._name

            @name.setter
            def name(self, name):
                self._name = name


        class Email(object):
            def __init__(self):
                self._email = str()

            @property
            def email(self):
                return self._email

            @email.setter
            def email(self, email):
                self._email = email


        class Password(object):
            def __init__(self):
                self._password = str()

            @property
            def password(self):
                return self._password

            @password.setter
            def password(self, password):
                self._password = password

        class Roles(object):
            def __init__(self):
                self._roles = list()

            @property
            def roles(self):
                return self._roles

            @roles.setter
            def roles(self, roles):
                self._roles.append(roles)

    class Subscriptions(object):
        
        def __init__(self, payload):

            if payload == {}:
                return

            nameObj = resourcePaylod.Subscriptions.Name()
            typeObj = resourcePaylod.Subscriptions.Type()
            settingsObj = resourcePaylod.Subscriptions.Settings()
            channelTypeObj = resourcePaylod.Subscriptions.ChannelType()
            channelIdObj = resourcePaylod.Subscriptions.ChannelId()

            if 'alert_name' in payload:
                setattr(nameObj, 'name', payload['alert_name'])
            self.name = getattr(nameObj, 'name', None)

            if 'type' in payload:
                setattr(typeObj, 'type', payload['type'])
                setattr(settingsObj, 'alert_me', payload['alert_me'])
                setattr(settingsObj, 'duration', payload['duration'])
                if 'org_id' in payload and payload['org_id'] is not None:
                    setattr(settingsObj, 'org_id', payload['org_id'])
                    getattr(settingsObj, 'org_id')
                if 'node_id' in payload and payload['node_id'] is not None:
                    setattr(settingsObj, 'node_id', payload['node_id'])
                    getattr(settingsObj, 'node_id')
                if 'pod_id' in payload and payload['pod_id'] is not None:
                    setattr(settingsObj, 'pod_id', payload['pod_id'])
                    getattr(settingsObj, 'pod_id')
                if 'network_id' in payload and payload['network_id'] is not None:
                    setattr(settingsObj, 'network_id', payload['network_id'])
                    getattr(settingsObj, 'network_id')
                if 'tunnel_id' in payload and payload['tunnel_id'] is not None:
                    setattr(settingsObj, 'tunnel_id', payload['tunnel_id'])
                    getattr(settingsObj, 'tunnel_id')
            self.type = getattr(typeObj, 'type', None)
            self.settings = getattr(settingsObj, 'alert_me', None)

            if 'channel_type' in payload:
                setattr(channelTypeObj, 'channel_type', payload['channel_type'])
            self.channel_type = getattr(channelTypeObj, 'channel_type', None)

            if 'channel_id' in payload:
                setattr(channelIdObj, 'channel_id', payload['channel_id'])
            self.channel_id = getattr(channelIdObj, 'channel_id', None)

        class Name(object):
            def __init__(self):
                self._name = str()

            @property
            def name(self):
                return self._name

            @name.setter
            def name(self, name):
                self._name = name

        class Type(object):
            def __init__(self):
                self._type = str()

            @property
            def type(self):
                return self._type

            @type.setter
            def type(self, type):
                self._type = type

        class Settings(object):
            def __init__(self):
                self._settings = dict()

            @property
            def alert_me(self):
                return self._settings

            @alert_me.setter
            def alert_me(self, alert_me):
                self._settings["alert_me"] = alert_me

            @property
            def duration(self):
                return self._settings

            @duration.setter
            def duration(self, duration):
                self._settings["duration"] = duration

            @property
            def include_child(self):
                return self._settings

            @include_child.setter
            def include_child(self, include_child):
                self._settings["include_child"] = include_child

            @property
            def org_id(self):
                return self._settings

            @org_id.setter
            def org_id(self, org_id):
                self._settings["org_id"] = org_id


            @property
            def node_id(self):
                return self._settings

            @node_id.setter
            def node_id(self, node_id):
                self._settings["node_id"] = node_id

            @property
            def pod_id(self):
                return self._settings

            @pod_id.setter
            def pod_id(self, pod_id):
                self._settings["pod_id"] = pod_id

            @property
            def network_id(self):
                return self._settings

            @network_id.setter
            def network_id(self, network_id):
                self._settings["network_id"] = network_id

            @property
            def tunnel_id(self):
                return self._settings

            @tunnel_id.setter
            def tunnel_id(self, tunnel_id):
                self._settings["tunnel_id"] = tunnel_id

        class ChannelType(object):
            def __init__(self):
                self._channel_type = str()

            @property
            def channel_type(self):
                return self._channel_type

            @channel_type.setter
            def channel_type(self, channel_type):
                self._channel_type = channel_type

        class ChannelId(object):
            def __init__(self):
                self._channel_id = str()

            @property
            def channel_id(self):
                return self._channel_id

            @channel_id.setter
            def channel_id(self, channel_id):
                self._channel_id = channel_id


    class Webhook(object):

        def __init__(self, payload):

            webhookName_Obj = resourcePaylod.Webhook.WebhookName()
            webhookUrl_Obj = resourcePaylod.Webhook.WebhookUrl()
            webhookSecret_Obj = resourcePaylod.Webhook.WebhookSecret()
            webhookHeaders_Obj = resourcePaylod.Webhook.WebhookHeaders()
            labelObj = resourcePaylod.Metadata.Label()

            if 'name' in payload and payload['name']:
                setattr(webhookName_Obj, 'name', payload['name'])
            else:
                setattr(webhookName_Obj, 'name', "")
            self.name = getattr(webhookName_Obj, 'name')

            if 'url' in payload and payload['url']:
                setattr(webhookUrl_Obj, 'url', payload['url'])
            else:
                setattr(webhookUrl_Obj, 'url', "")
            self.url = getattr(webhookUrl_Obj, 'url')

            if 'secret' in payload and payload['secret']:
                setattr(webhookSecret_Obj, 'secret', payload['secret'])
            else:
                setattr(webhookSecret_Obj, 'secret', "")
            self.secret = getattr(webhookSecret_Obj, 'secret')

            if 'headers' in payload and payload['headers']:
                setattr(webhookHeaders_Obj, 'headers', payload['headers'])
            self.headers = getattr(webhookHeaders_Obj, 'headers')

            if 'label' in payload and payload["label"] is not None and \
                            payload["label"].title() != "None" and payload["label"]:
                setattr(labelObj, "metadata", payload["label"])
            self.metadata = getattr(labelObj, 'metadata', {"labels": {}})

        class WebhookName(object):
            def __init__(self):
                self._name = str()

            @property
            def name(self):
                return self._name

            @name.setter
            def name(self, name):
                self._name = name

        class WebhookUrl(object):
            def __init__(self):
                self._url = str()

            @property
            def url(self):
                return self._url

            @url.setter
            def url(self, url):
                self._url = url

        class WebhookSecret(object):
            def __init__(self):
                self._secret = str()

            @property
            def secret(self):
                return self._secret

            @secret.setter
            def secret(self, secret):
                self._secret = secret

        class WebhookHeaders(object):
            def __init__(self):
                self._headers = dict()

            @property
            def headers(self):
                return self._headers

            @headers.setter
            def headers(self, headers):
                self._headers = headers

    class WebhookTest(object):

        def __init__(self, payload):
            webhookAlertType_Obj = resourcePaylod.WebhookTest.WebhookAlertType()

            if 'alert_type' in payload and payload['alert_type']:
                setattr(webhookAlertType_Obj, 'alert_type', payload['alert_type'])
            else:
                setattr(webhookAlertType_Obj, 'alert_type', "")
            self.alert_type = getattr(webhookAlertType_Obj, 'alert_type')

        class WebhookAlertType(object):
            def __init__(self):
                self._alert_type = dict()

            @property
            def alert_type(self):
                return self._alert_type

            @alert_type.setter
            def alert_type(self, alert_type):
                self._alert_type = alert_type
    
    class SshKey(object):
        def __init__(self, payload):
            sshkeyName_Obj = resourcePaylod.SshKey.keyName()
            if 'name' in payload and payload['name']:
                setattr(sshkeyName_Obj, 'name', payload['name'])
                self.name = getattr(sshkeyName_Obj, 'name')

            pubkey_Obj = resourcePaylod.SshKey.pubKey()
            if 'public_key' in payload and payload['public_key']:
                setattr(pubkey_Obj, 'public_key', payload['public_key'])
                self.public_key = getattr(pubkey_Obj, 'public_key')

        class keyName(object):
            def __init__(self):
                self._name = str()

            @property
            def name(self):
                return self._name

            @name.setter
            def name(self, name):
                self._name = name

        class pubKey(object):
            def __init__(self):
                self._key = str()

            @property
            def public_key(self):
                return self._key

            @public_key.setter
            def public_key(self, name):
                self._key = name

    class OrgPolicy(object):
        def __init__(self, payload):
            two_factor_Obj = resourcePaylod.OrgPolicy.TOTP()
            if 'two_factor' in payload and payload['two_factor'] is not None:
                setattr(two_factor_Obj, 'two_factor', payload['two_factor'])
                self.two_factor = getattr(two_factor_Obj, 'two_factor')

            headless_mode_Obj = resourcePaylod.OrgPolicy.HeadlessMode()
            if 'headless_mode' in payload and payload['headless_mode'] is not None:
                setattr(headless_mode_Obj, 'headless_mode', payload['headless_mode'])
                self.headless_mode = getattr(headless_mode_Obj, 'headless_mode')

            vlan_support_Obj = resourcePaylod.OrgPolicy.VLAN()
            if 'vlan_support' in payload and payload['vlan_support'] is not None:
                setattr(vlan_support_Obj, 'vlan_support', payload['vlan_support'])
                self.vlan_support = getattr(vlan_support_Obj, 'vlan_support')

            software_upgrade_channel_Obj = resourcePaylod.OrgPolicy.Upgrade()
            if 'software_upgrade_channel' in payload and payload['software_upgrade_channel'] is not None:
                setattr(software_upgrade_channel_Obj, 'software_upgrade_channel', payload['software_upgrade_channel'])
                self.software_upgrade_channel = getattr(software_upgrade_channel_Obj, 'software_upgrade_channel')

            apikey_Obj = resourcePaylod.OrgPolicy.APIKEY()
            if 'apikey' in payload and payload['apikey'] is not None:
                setattr(apikey_Obj, 'apikey', payload['apikey'])
                self.apikey = getattr(apikey_Obj, 'apikey')

            one_arm_mode_Obj = resourcePaylod.OrgPolicy.ONEARM()
            if 'one_arm_mode' in payload and payload['one_arm_mode'] is not None:
                setattr(one_arm_mode_Obj, 'one_arm_mode', payload['one_arm_mode'])
                self.one_arm_mode = getattr(one_arm_mode_Obj, 'one_arm_mode')

            branding_Obj = resourcePaylod.OrgPolicy.WHITELABLE()
            if 'branding' in payload and payload['branding'] is not None:
                setattr(branding_Obj, 'branding', payload['branding'])
                self.branding = getattr(branding_Obj, 'branding')

            cluster_Obj = resourcePaylod.OrgPolicy.Cluster()
            if 'cluster' in payload and payload['cluster'] is not None:
                setattr(cluster_Obj, 'cluster', payload['cluster'])
                self.cluster = getattr(cluster_Obj, 'cluster')

        class TOTP(object):
            def __init__(self):
                self._value = {"enable" : bool()}

            @property
            def two_factor(self):
                return self._value

            @two_factor.setter
            def two_factor(self, value):
                self._value["enable"] = value

        class HeadlessMode(object):
            def __init__(self):
                self._value = {"enable": bool()}

            @property
            def headless_mode(self):
                return self._value

            @headless_mode.setter
            def headless_mode(self, value):
                self._value["enable"] = value


        class VLAN(object):
            def __init__(self):
                self._value = {"enable": bool()}

            @property
            def vlan_support(self):
                return self._value

            @vlan_support.setter
            def vlan_support(self, value):
                self._value["enable"] = value

        class Upgrade(object):
            def __init__(self):
                self._value = {"channel": str()}

            @property
            def software_upgrade_channel(self):
                return self._value

            @software_upgrade_channel.setter
            def software_upgrade_channel(self, value):
                self._value["channel"] = value.upper()


        class APIKEY(object):
            def __init__(self):
                self._value = {"enable": bool()}

            @property
            def apikey(self):
                return self._value

            @apikey.setter
            def apikey(self, value):
                self._value["enable"] = value

        class ONEARM(object):
            def __init__(self):
                self._value = {"enable": bool()}

            @property
            def one_arm_mode(self):
                return self._value

            @one_arm_mode.setter
            def one_arm_mode(self, value):
                self._value["enable"] = value


        class WHITELABLE(object):
            def __init__(self):
                self._value = {"enable": bool()}

            @property
            def branding(self):
                return self._value

            @branding.setter
            def branding(self, value):
                self._value["enable"] = value

        class Cluster(object):
            def __init__(self):
                self._value = {"enable": bool()}

            @property
            def cluster(self):
                return self._value

            @cluster.setter
            def cluster(self, value):
                self._value["enable"] = value

    class Cluster(object):
        def __init__(self, payload):

            name_Obj = resourcePaylod.Cluster.ClusterName()
            if 'name' in payload and payload['name'] is not None:
                setattr(name_Obj, 'name', payload['name'])
                self.name = getattr(name_Obj, 'name')

            labelObj = resourcePaylod.Metadata.Label()
            if 'labels' in payload and payload["labels"] is not None and \
                            payload["labels"].title() != "None" and payload["labels"]:
                setattr(labelObj, "metadata", payload["labels"])
            self.metadata = getattr(labelObj, 'metadata', {"labels": {}})

            nodesObj = resourcePaylod.Cluster.Nodes()
            if 'nodes' in payload and payload['nodes'] is not None and payload['nodes']:
                setattr(nodesObj, "nodes", payload["nodes"])
            self.nodes = getattr(nodesObj, 'nodes', [])

            InstanceIdObj = resourcePaylod.Cluster.InstanceId()
            if 'instance_id' in payload and payload['instance_id'] is not None and payload['instance_id']:
                setattr(InstanceIdObj, "instance_id", payload["instance_id"])
                self.config = getattr(InstanceIdObj, 'instance_id')

            containerTimeZoneObj = resourcePaylod.Cluster.ContainerTimeZone()
            if 'container_timezone' in payload and payload['container_timezone'] is not None:
                setattr(containerTimeZoneObj, 'container_timezone', payload['container_timezone'])
                self.container_timezone = getattr(containerTimeZoneObj, 'container_timezone')

        class ClusterName(object):
            def __init__(self):
                self._value = str()

            @property
            def name(self):
                return self._value

            @name.setter
            def name(self, value):
                self._value = value

        class Nodes(object):
            def __init__(self):
                self._value = list()

            @property
            def nodes(self):
                return self._value

            @nodes.setter
            def nodes(self, value):
                if isinstance(value, list):
                    for nodes in value:
                        _temp = {"node_id": str(), "config": dict()}
                        if 'node_id' in nodes:
                            _temp.update({"node_id":nodes['node_id']})
                        if 'priority' in nodes:
                            _temp['config'].setdefault("priority", nodes['priority'])
                        else:
                            _temp['config'].setdefault("priority", 100)
                        if 'is_candidate' in nodes:
                            _temp['config'].setdefault("is_candidate", nodes['is_candidate'])
                        else:
                            _temp['config'].setdefault("is_candidate", False)
                        self._value.append(_temp)

        class InstanceId(object):
            def __init__(self):
                self._value = {"instance_id" : 100}

            @property
            def instance_id(self):
                return self._value

            @instance_id.setter
            def instance_id(self, value):
                self._value['instance_id'] = value

        class ContainerTimeZone(object):
            def __init__(self):
                self._value = str()

            @property
            def container_timezone(self):
                return self._value

            @container_timezone.setter
            def container_timezone(self, value):
                self._value = value

    class DownloadEvent(object):
        def __init__(self, payload):
            if payload == {}:
                return

            orgId_Obj = resourcePaylod.Organisation.orgId()
            if 'org_id' in payload and payload['org_id'] is not None:
                setattr(orgId_Obj, 'org_id', payload['org_id'])
                self.org_id = getattr(orgId_Obj, 'org_id')

            if 'node_id' in payload and payload['node_id'] is not None:
                self.node_id = payload['node_id']

            if 'cluster_id' in payload and payload['cluster_id'] is not None:
                self.cluster_id = payload['cluster_id']

            if 'resource_group' in payload and payload['resource_group'] is not None:
                self.resource_group = payload['resource_group']

            if 'own' in payload and payload['own'] is not None:
                self.own = payload['own']

            if 'start_date' in payload and payload['start_date'] is not None:
                self.start_date = payload['start_date']

            if 'end_date' in payload and payload['end_date'] is not None:
                self.end_date = payload['end_date']

    class DownloadActivity(object):
        def __init__(self, payload):
            if payload == {}:
                return

            orgId_Obj = resourcePaylod.Organisation.orgId()
            if 'org_id' in payload and payload['org_id'] is not None:
                setattr(orgId_Obj, 'org_id', payload['org_id'])
                self.org_id = getattr(orgId_Obj, 'org_id')

            if 'start_date' in payload and payload['start_date'] is not None:
                self.start_date = payload['start_date']

            if 'end_date' in payload and payload['end_date'] is not None:
                self.end_date = payload['end_date']

            if 'own' in payload and payload['own'] is not None:
                self.own = payload['own']

    class iNodeCli(object):
        def __init__(self, action, payload):
            if ( action == "set" or action == "unset" ) and \
                    (payload['command'] == "timeserver" or
                             payload['command'] == 'nameserver'):
                self.action = action
                self.ip_address = payload['params']['ip_address']
            if action == "set" and payload['command'] == "proxy":
                self.action = action
                self.protocol = "HTTPS"
                if 'username' in payload['params']:
                    self.url = "{}@{}".format(payload['params']['username'], payload['params']['url'])
                    self.password = payload['params']['password']
                else:
                    self.url = payload['params']['url']
            if action == "unset" and payload['command'] == "proxy":
                self.action = action
                self.protocol = "HTTPS"
            if action == "set" and payload['command'] == "wan_ip":
                self.action = action
                self.ip_address = payload['params']['ip_address']
                self.netmask = payload['params']['netmask']
                self.gateway = payload['params']['gateway']
            if action == "set" and payload['command'] == "wan_vlan":
                self.action = action
                self.vlan_id = payload['params']['vlan_id']
            if action == "set" and payload['command'] == "mgmt_ip":
                self.action = action
                self.ip_address = payload['params']['ip_address']
                self.netmask = payload['params']['netmask']
            if action == "unset" and \
                    (payload['command'] == "wan_ip" or
                             payload['command'] == "mgmt_ip" or
                             payload['command'] == "wan_vlan"):
                self.action = action
