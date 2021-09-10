from pulumi import ResourceOptions
import pulumi_azure_native.containerservice as container_service

def managed_cluster(stem, rg=None, clientID=None, secret=None, provider=None,depends_on=None):

    aks_cluster = container_service.ManagedCluster(stem,
        resource_group_name=rg,
        agent_pool_profiles=[{
            'count': 2,
            'max_pods': 110,
            'mode': 'System',
            'name': 'agentpool',
            'node_labels': {},
            'os_disk_size_gb': 30,
            'os_type': 'Linux',
            'type': 'VirtualMachineScaleSets',
            'vm_size': 'Standard_D2_v2',
        }],
        dns_prefix='nv',
        service_principal_profile=container_service.ManagedClusterServicePrincipalProfileArgs(
            client_id=clientID,
            secret=secret,
        ),
        opts=ResourceOptions(provider=provider, depends_on=depends_on)
    )

    return aks_cluster