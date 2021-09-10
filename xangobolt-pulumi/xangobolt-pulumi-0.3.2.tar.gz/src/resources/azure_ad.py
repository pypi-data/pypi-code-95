from pulumi import ResourceOptions
import pulumi_azure_native.network as network
import pulumi_azuread as azad

def application(stem, provider=None, depends_on=None):
    az_app = azad.Application(f'app-{stem}',
        display_name=stem,
        opts=ResourceOptions(provider=provider, parent=self, depends_on=depends_on),
    )
    return az_app

def service_principle(stem,app_id, provider=None, depends_on=None):
    app_sp = azad.ServicePrincipal(f'sp-{stem}',
        application_id = app_id,
        opts=ResourceOptions(provider=provider,parent=self, depends_on=depends_on),
    )
    return app_sp

def service_principle_password(stem, sp_id, provider=None, depends_on=None):
    sp_pword = azad.ServicePrincipalPassword(f'pw-{stem}',
        service_principal_id = sp_id,
        opts=ResourceOptions(provider=provider,parent=self, depends_on=depends_on),
    )
    return sp_pword