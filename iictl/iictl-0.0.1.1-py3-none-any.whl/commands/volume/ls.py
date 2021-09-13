import click
from tabulate import tabulate
from iictl.commands.volume.main import volume
from iictl.crud.persistent_volume_claim import list_persistent_volume_claim
from iictl.utils.click import global_option

@volume.command(help='list volume')
@click.option('-n', '--namespace', type=str, help='name of namespace', callback=global_option)
def ls(namespace):
    volume_list = list_persistent_volume_claim(
        namespace=namespace,
    )
    volume_list = [{
        'name': it.metadata.name,
        'size': it.spec.resources.requests['storage'],
        'protection': it.metadata.annotations['deep.est.ai/volume-protection'] if 'deep.est.ai/volume-protection' in it.metadata.annotations else "false",
    } for it in volume_list.items]
    
    click.echo(tabulate(volume_list, headers='keys'))