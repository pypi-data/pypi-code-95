from pulumi import ComponentResource, ResourceOptions, StackReference
from pulumi.resource import export
from pulumi_azuread import provider
from ..resources import azure_ad, container_service, resource_group
import pulumi
from pulumi import Output

class AKS(ComponentResource):
    def __init__(self, name: str, props: None, opts:  ResourceOptions = None):
        super().__init__('AKS', name, {}, opts)

        Resources = [azure_ad]

        for resource in Resources:
            resource.self = self
            resource.tags = props.tags

        # Create Azure Application
        app = azure_ad.application(name, provider=opts.providers.get('aad'))

        # Create Service Principle
        sp = azure_ad.service_principle(name, app_id=app.application_id, provider=opts.providers.get('aad'))

        # Create Service Principle Password
        sp_pword = azure_ad.service_principle_password(name, sp_id=sp.id, provider=opts.providers.get('aad'))

        # Create Resource Group
        rg = resource_group.resource_group(name, props, provider=opts.providers.get('az'))

        # Container Service
        mc = container_service.managed_cluster('novari', rg.name, clientID=app.application_id, secret=sp_pword.value, provider=opts.providers.get('az'))