import click
from iictl.commands.volume.main import volume
from iictl.crud.persistent_volume_claim import patch_persistent_volume_claim
from iictl.utils.exception import NotFoundError
from iictl.utils.click import global_option
from iictl.utils.parse import verify_object_name

@volume.command(help='unprotect volume')
@click.option('-n', '--namespace', type=str, help='name of namespace', callback=global_option)
@click.argument('name')
def unprotect(name, namespace):
    if not verify_object_name(name):
        click.echo('wrong object name')
        return 
    
    try:
        patch_persistent_volume_claim(
            name=name,
            namespace=namespace,
            body={'metadata':{'annotations':{'deep.est.ai/volume-protection': 'false'}}}
        )
    except NotFoundError as e:
        click.echo(f'volume "{name}" not found')
        exit(1)

    
    click.echo(f'A volume {name} was unprotected.')