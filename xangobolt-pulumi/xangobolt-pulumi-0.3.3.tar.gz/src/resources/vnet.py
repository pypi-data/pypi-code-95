from pulumi import ResourceOptions
import pulumi_azure_native.network as network

# Variables that may need to be injected before calling functions:
# vdc.location = props.location
# vdc.resource_group_name = props.resource_group_name
# vdc.s = props.separator
# vdc.self = self
# vdc.suffix = props.suffix
# vdc.tags = props.tags

def virtual_network(
        stem, 
        props=None, 
        address_spaces=None, 
        provider=None, 
        depends_on=None,
):
    vn = network.VirtualNetwork(
        f'vn-{stem}',
        virtual_network_name=f'vn-{stem}',
        location=props.location, 
        resource_group_name=props.resource_group_name,
        address_space=network.AddressSpaceArgs(
            address_prefixes=address_spaces,
        ),
        tags=props.tags,
        opts=ResourceOptions(provider=provider,parent=self, depends_on=depends_on),
    )
    return vn


def vnet_peering(
        stem,
        rg,
        virtual_network_name,
        peer,
        remote_virtual_network_id,
        allow_forwarded_traffic=None,
        allow_gateway_transit=None,
        use_remote_gateways=None,
        provider=None,
        depends_on=None,
):
    vnp = network.VirtualNetworkPeering(
        f'vnpr-{stem}',
        name=f'vnpr-{stem}',
        resource_group_name=rg,
        virtual_network_name=virtual_network_name,
        remote_virtual_network=network.SubResourceArgs(
            id=remote_virtual_network_id
        ),
        allow_forwarded_traffic=allow_forwarded_traffic,
        allow_gateway_transit=allow_gateway_transit,
        use_remote_gateways=use_remote_gateways,
        allow_virtual_network_access=True,
        opts=ResourceOptions(provider=provider,parent=self, depends_on=depends_on),
    )
    return vnp


def subnet(
        stem,
        props,
        virtual_network_name,
        address_prefix,
        route_table_id,
        provider=None,
        depends_on=None,
):
    sn = network.Subnet(
        f'sn-{stem}',
        name=f'sn-{stem}',
        resource_group_name=props.resource_group_name,
        virtual_network_name=virtual_network_name,
        address_prefix=address_prefix,
        route_table=network.RouteTableArgs(
            id=route_table_id,
        ),
        opts=ResourceOptions(provider=provider, parent=self, depends_on=depends_on),
    )
    return sn

def subnet_special(
        stem,
        name,
        props,
        virtual_network_name,
        address_prefix,
        route_table_id,
        provider=None,
        depends_on=None,
):
    sn = network.Subnet(
        f'sn-{stem}',
        name=name,
        subnet_name=name,
        resource_group_name=props.resource_group_name,
        virtual_network_name=virtual_network_name,
        address_prefix=address_prefix,
        route_table=network.RouteTableArgs(
            id=route_table_id,
        ),
        opts=ResourceOptions(
            parent=self,
            delete_before_replace=True,
            provider=provider,
            depends_on=depends_on,
        ),
    )
    return sn


def pubIP(
        stem,
        props,
        provider=None,
        depends_on=None,
):
    pubip = network.PublicIPAddress(
        f'pi-{stem}',
        public_ip_address_name=f'pi-{stem}',
        location=props.location,
        resource_group_name=props.resource_group_name,
        public_ip_allocation_method=network.IPAllocationMethod.DYNAMIC,
        opts=ResourceOptions(
            parent=self,
            delete_before_replace=True,
            provider=provider,
            depends_on=depends_on,
        ),
    )
    return pubip


def network_interface(
        stem,
        props,
        pubip_id=None,
        provider=None,
        depends_on=None,
):
    net_int = network.NetworkInterface(
        f'ni-{stem}',
        network_interface_name=f'ni-{stem}',
        resource_group_name=props.resource_group_name,
        ip_configurations=[network.NetworkInterfaceIPConfigurationArgs(
            name="niipcfg",
            subnet=network.SubnetArgs(id=props.subnetid),
            private_ip_allocation_method=network.IPAllocationMethod.DYNAMIC,
            public_ip_address=network.PublicIPAddressArgs(id=pubip_id),
        )],
        opts=ResourceOptions(
            parent=self,
            delete_before_replace=True,
            provider=provider,
            depends_on=depends_on,
        ),
    )
    return net_int