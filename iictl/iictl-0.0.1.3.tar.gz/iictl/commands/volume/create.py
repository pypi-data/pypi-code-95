import click
from iictl.commands.volume.main import volume
from iictl.format.persistent_volume_claim import get_persistent_volume_claim_format
from iictl.crud.persistent_volume_claim import create_persistent_volume_claim
from iictl.utils.exception import AlreadyExistError
from iictl.utils.click import global_option
from iictl.utils.parse import verify_object_name

@volume.command(help='create volume')
@click.option('-n', '--namespace', type=str, help='name of namespace', callback=global_option)
@click.argument('name')
@click.argument('size')
def create(name, namespace, size):
    if not verify_object_name(name):
        click.echo('wrong object name')
        return 
    
    pvc = get_persistent_volume_claim_format(
        name=name,
        size=size,
    )
    
    try:
        create_persistent_volume_claim(
            name=name,
            namespace=namespace,
            body=pvc,
        )
        click.echo(f'volume "{name}" creation was requested.')
    except AlreadyExistError as e:
        click.echo(f'volume "{name}" already exist')

        