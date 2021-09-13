import click
from tabulate import tabulate
from iictl.commands import cli
from iictl.crud.integrated_instance import list_integrated_instance
from iictl.utils.click import global_option

@cli.command(help='print instance list')
@click.option('-n', '--namespace', type=str, help='name of namespace', callback=global_option)
def ps(namespace):
    iis = list_integrated_instance(
        namespace=namespace,
    )
    
    table = [{
        'name': ii['metadata']['name'],
        'image': ii['spec']['image'],
        'status': 'Unknown' if 'status' not in ii or 'deploymentStatus' not in ii['status'] else ii['status']['deploymentStatus'], # TODO
    } for ii in iis['items']]
        
    click.echo(tabulate(table, headers='keys'))