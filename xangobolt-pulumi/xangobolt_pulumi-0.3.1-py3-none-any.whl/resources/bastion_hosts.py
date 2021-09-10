from pulumi import ResourceOptions
import pulumi_azure_native.network as network


def bastion_host(stem, ab_snet, depends_on=None):

    ab_pip = network.PublicIPAddress(
        f'bhpip-{stem}',
        resource_group_name=resource_group_name,
        sku=network.PublicIPAddressSkuArgs(
            name=network.PublicIPAddressSkuName.STANDARD,
        ),
        public_ip_allocation_method=network.IPAllocationMethod.STATIC,
        tags=tags,
        opts=ResourceOptions(parent=self, depends_on=depends_on),
    )
    ab = network.BastionHost(
        f'bh-{stem}',
        resource_group_name=resource_group_name,
        ip_configurations=[network.BastionHostIPConfigurationArgs(
            name=f'bhipcfg{stem}',
            public_ip_address=network.PublicIPAddressArgs(
                id=ab_pip.id,
            ),
            subnet=network.SubnetArgs(
                id=ab_snet,
            ),
        )],
        tags=tags,
        opts=ResourceOptions(parent=self, depends_on=depends_on),
    )
    return ab