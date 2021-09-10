from ipaddress import ip_network, ip_address
from pulumi import ComponentResource, ResourceOptions, StackReference
from ..resources import route_table, vnet, firewall, vpn_gateway, bastion_hosts, resource_group


class Hub(ComponentResource):
    def __init__(self, name: str, props: None, opts: ResourceOptions = None):
        super().__init__('vdc:network:Hub', name, {}, opts)

        # Create Hub resource group
        # hub_rg = resource_group.resource_group('Hub', props, parent = self)

        hubResources = [route_table, vnet, firewall, vpn_gateway, bastion_hosts, resource_group]

        for resource in hubResources:
            resource.location = props.location
            resource.resource_group_name = props.resource_group_name
            resource.self = self
            resource.tags = props.tags

        # set the separator to be used in resource names
        s = props.separator

        # Calculate the subnets in the hub_address_space
        hub_network = ip_network(props.hub_address_space)
        if hub_network.prefixlen < 20:
            sub_diff = int((hub_network.max_prefixlen - hub_network.prefixlen) / 2)
        else:
            sub_diff = 25 - hub_network.prefixlen  # minimum /25 subnet
        subnets = hub_network.subnets(prefixlen_diff=sub_diff)
        first_snet = next(subnets)  # first subnet reserved for special uses
        # first_sn = next_sn.subnets(new_prefix=26)  # split it into /26 subnets
        firewallmgmt_snet = str(next(subnets))
        firewall_snet = str(next(subnets))  # Azure Firewall Subnet
        vpngw_snet = str(next(subnets))  # Azure VPN Gateway Subnet
        bastion_snet = str(next(subnets))  # Azure Bastion Subnet

        # Azure Virtual Network to which spokes will be peered
        # separate address spaces to simplify custom routing
        hub = vnet.virtual_network(
            f'{props.orgName}-Hub', 
            props,
            [
                #props.firewall_address_space,
                props.hub_address_space,
            ],
            )

        # AzureFirewallManagementSubnet and Route Table
        # https://docs.microsoft.com/en-us/azure/firewall/forced-tunneling
        hub_fwmgmt_rt = route_table.route_table(
            stem=f'firewallmgmt',
            disable_bgp_route_propagation=True,  # required
            depends_on=[hub]
        )

        # only a default route to the Internet is permitted
        hub_fwmgmt_route = route_table.route_to_internet(
            stem=f'firewallmgmt-internet',
            route_table_name=hub_fwmgmt_rt.name,
            depends_on=[hub_fwmgmt_rt]
        )

        hub_fwmgmt_snet = vnet.subnet_special(
            stem=f'firewallmgmt',
            name='AzureFirewallManagementSubnet',  # name required
            props=props,
            virtual_network_name=hub.name,
            address_prefix=firewallmgmt_snet,
            route_table_id=hub_fwmgmt_rt.id,
            depends_on=[hub_fwmgmt_rt, hub_fwmgmt_route],
        )

        # AzureFirewallSubnet Route Table 
        hub_firewall_rt = route_table.route_table(
            stem=f'firewall',
            disable_bgp_route_propagation=False,
            depends_on=[hub],
        )

        # default route either direct to Internet or forced tunnel
        # turn off SNAT if the next_hop_ip_address is public
        # https://docs.microsoft.com/en-us/azure/firewall/snat-private-range
        private_ranges = 'IANAPrivateRanges'
        if not props.forced_tunnel:
            hub_firewall_route = route_table.route_to_internet(
                stem=f'firewall-internet',
                route_table_name=hub_firewall_rt.name,
                depends_on=[hub_firewall_rt]
            )
        else:
            hub_firewall_route = route_table.route_to_virtual_appliance(
                stem=f'firewall-tunnel',
                route_table_name=hub_firewall_rt.name,
                address_prefix='0.0.0.0/0',
                next_hop_ip_address=props.forced_tunnel,
                depends_on=[hub_firewall_rt]
            )
            ft_ip = ip_address(props.forced_tunnel)
            if not ft_ip.is_private:
                private_ranges = '0.0.0.0/0'

        
        hub_firewall_snet = vnet.subnet_special(
            stem=f'firewall',
            name='AzureFirewallSubnet',  # name required
            props=props,
            virtual_network_name=hub.name,
            address_prefix=firewall_snet,
            route_table_id=hub_firewall_rt.id,
            depends_on=[hub_firewall_rt, hub_firewall_route],
        )

        # Azure Firewall
        hub_firewall = firewall.firewall(
            stem=f'Hub',
            fw_sn_id=hub_firewall_snet.id,
            fwm_sn_id=hub_fwmgmt_snet.id,
            private_ranges=private_ranges,
            depends_on=[hub_firewall_snet, hub_fwmgmt_snet],
        )

        # wait for the private ip address of the firewall to become available
        hub_firewall_ip = hub_firewall.ip_configurations.apply(
            lambda ipc: ipc[0].private_ip_address
        )

        # It is very important to ensure that there is never a route with an
        # address_prefix which covers the AzureFirewallSubnet.


        # GatewaySubnet and Route Table
        hub_gateway_rt = route_table.route_table(
            stem=f'gateway',
            disable_bgp_route_propagation=False,
            depends_on=[hub],
        )

        # protect intra-GatewaySubnet traffic from being redirected:
        hub_gw_2_gw_route = route_table.route_to_virtual_network(
            stem=f'gateway-gateway',
            route_table_name=hub_gateway_rt.name,
            address_prefix=vpngw_snet,
            depends_on=[hub_gateway_rt]
        )

        # redirect traffic from gateways to hub via firewall
        hub_gw_2_hub_route = route_table.route_to_virtual_appliance(
            stem=f'gateway-hub',
            route_table_name=hub_gateway_rt.name,
            address_prefix=props.hub_address_space,
            next_hop_ip_address=hub_firewall_ip,
            depends_on=[hub, hub_gateway_rt]
        )

        # Create gateway Subnet
        hub_gateway_snet = vnet.subnet_special(
            stem=f'gateway',
            name='GatewaySubnet',  # name required
            props=props,
            virtual_network_name=hub.name,
            address_prefix=vpngw_snet,
            route_table_id=hub_gateway_rt.id,
            depends_on=[hub_gateway_rt, hub_gw_2_gw_route, hub_gw_2_hub_route],
        )

        # Create VPN Gateway
        hub_vpn_gateway = vpn_gateway.vpn_gateway(
            stem='Hub',
            subnet_id=hub_gateway_snet.id,
            depends_on=[hub_gateway_snet],
        )

         # Route Table to be associated with all hub shared services subnets
        hub_sharedservices_rt = route_table.route_table(
            stem=f'shared-services',
            disable_bgp_route_propagation=True,
            depends_on=[hub_vpn_gateway],
        )

        # default route from hub via the firewall
        hub_sharedservies_2_inet = route_table.route_to_virtual_appliance(
            stem=f'sharedsrv-inet',
            route_table_name=hub_sharedservices_rt.name,
            address_prefix='0.0.0.0/0',
            next_hop_ip_address=hub_firewall_ip,
            depends_on=[hub_sharedservices_rt]
        )

        # redirect traffic from hub to gateways via the firewall
        hub_sharedservices_2_gw = route_table.route_to_virtual_appliance(
            stem=f'sharedsrv-gw',
            route_table_name=hub_sharedservices_rt.name,
            address_prefix=vpngw_snet,
            next_hop_ip_address=hub_firewall_ip,
            depends_on=[hub_sharedservices_rt]
        )
        # shared services subnets starting with the second subnet
        for subnet in props.subnets:
            next_sn = next(subnets)
            hub_sn = vnet.subnet(  # ToDo add NSG
                stem=f'{subnet[0]}',
                virtual_network_name=hub.name,
                address_prefix=str(next_sn),
                route_table_id=hub_sharedservices_rt.id,
                depends_on=[hub_sharedservices_rt, hub_sharedservies_2_inet, hub_sharedservices_2_gw],
            )


        # Azure Bastion subnet and host (optional)
        if props.azure_bastion:
            # Create Azure Bastion Subnet
            hub_bastion_snet = vnet.subnet_special(
                stem=f'bastion',
                name='AzureBastionSubnet',
                props=props,
                virtual_network_name=hub.name,
                address_prefix=bastion_snet,
                depends_on=[hub_vpn_gateway],
                delete_before_replace=True,
            ),

            # Azure Bastion
            bastion = bastion_hosts.bastion_host(
                stem=f'Hub',
                ab_snet=hub_bastion_snet.id,
                depends_on=[hub_bastion_snet],
            )


        # VNet Peering between stacks using StackReference (optional)
        if props.peer:
            peer_hub_id = props.reference.get_output('hub_id')
            # VNet Peering (Global) in one direction from stack to peer
            hub_hub = vnet.vnet_peering(
                stem=props.stack,
                virtual_network_name=hub.name,
                peer=props.peer,
                remote_virtual_network_id=peer_hub_id,
                allow_forwarded_traffic=True,
                allow_gateway_transit=False,  # as both hubs have gateways
            )
            # need to invalidate system routes created by VNet Peering
            peer_fw_ip = props.reference.get_output('fw_ip')
            peer_hub_as = props.reference.get_output('hub_as')

            for route in [
                (f'gw{s}{props.peer}{s}hub', hub_gateway_rt.name, peer_hub_as),
                (f'ss{s}{props.peer}{s}hub', hub_sharedservices_rt.name, peer_hub_as),
            ]:
                vnet.route_to_virtual_appliance(
                    stem=route[0],
                    route_table_name=route[1],
                    address_prefix=route[2],
                    next_hop_ip_address=peer_fw_ip,
                )

                

        
        # assign properties to hub including from child resources
        self.address_space = props.hub_address_space  # used for routes to the hub
        # self.dmz_ar = dmz_ar  # used for routes to the hub
        #self.dmz_rt_name = hub_dmz_rt.name  # used to add routes to spokes
        #self.er_gw = hub_er_gw  # needed prior to VNet Peering from spokes
        self.fw = hub_firewall   # needed prior to VNet Peering from spokes
        self.fw_ip = hub_firewall_ip  # used for routes to the hub
        self.fw_rt_name = hub_firewall_rt.name  # used for route to the peered spokes
        self.gw_rt_name = hub_gateway_rt.name  # used to add routes to spokes
        self.id = hub.id  # exported and used for stack and spoke peering
        self.location = hub.location  # informational
        self.name = hub.name  # exported and used for spoke peering
        self.peer = props.peer  # informational
        self.resource_group_name = props.resource_group_name  # informational
        self.subnets = hub.subnets  # informational
        self.stack = props.stack  # informational
        self.stem = name  # used for VNet Peering from spokes
        self.ss_rt_name = hub_sharedservices_rt.name  # used to add routes to spokes
        self.tags = props.tags  # informational
        self.vpn_gw = hub_vpn_gateway  # needed prior to VNet Peering from spokes
        self.register_outputs({})