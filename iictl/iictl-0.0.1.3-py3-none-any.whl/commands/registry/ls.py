import click
from tabulate import tabulate
from iictl.commands.registry.main import registry
from iictl.crud.secret import list_secret
from iictl.utils.click import global_option

@registry.command(help='list registry')
@click.option('-n', '--namespace', type=str, help='name of namespace', callback=global_option)
def ls(namespace):
    secret_list = list_secret(
        namespace=namespace,
    )
    auth_list = [
        secret for secret in secret_list if secret['type'] == 'kubernetes.io/dockerconfigjson'
    ]
    
    auth_list = [{
        'name': it['metadata']['name'],
#         'size': it.spec.resources.requests['storage'],
#         'protection': it.metadata.annotations['deep.est.ai/volume-protection'] if 'deep.est.ai/volume-protection' in it.metadata.annotations else "false",
    } for it in auth_list]
    
    click.echo(tabulate(auth_list, headers='keys'))