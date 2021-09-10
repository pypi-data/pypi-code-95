from pulumi import ComponentResource, ResourceOptions, StackReference
from pulumi.resource import export
from pulumi_azuread import application
from resources import azure_ad
import pulumi
from pulumi import Output

class ServicePrinciple(ComponentResource):
    def __init__(self, name: str, props: None, opts:  ResourceOptions = None):
        super().__init__('ServicePrinciple', name, {}, opts)

        Resources = [azure_ad]

        for resource in Resources:
            resource.self = self
            resource.tags = props.tags

        # Create Azure Application
        app = azure_ad.application(name)

        # Create Service Principle
        sp = azure_ad.service_principle(f'sp-{name}', app_id=app.application_id)

        # Create Service Principle Password
        sp_pword = azure_ad.service_principle_password(f'pw-{name}', sp_id=sp.id)

        export('Service Principle ClientID', app.application_id)
        export("Service Principle Password", sp_pword.value)