import click
from iictl.commands.volume.main import volume
from iictl.crud.persistent_volume_claim import read_persistent_volume_claim
from iictl.crud.persistent_volume_claim import delete_persistent_volume_claim
from iictl.utils.exception import NotFoundError
from iictl.utils.click import global_option
from iictl.utils.parse import verify_object_name

@volume.command(help='remove volume') #really meant it?()
@click.option('-n', '--namespace', type=str, help='name of namespace', callback=global_option)
@click.argument('name')
def rm(name, namespace):
    if not verify_object_name(name):
        click.echo('wrong object name')
        return 
    
    try:
        pvc = read_persistent_volume_claim(
            name=name,
            namespace=namespace,
        )
    except NotFoundError as e:
        click.echo(f'volume "{name}" not found')
        exit(1)
    
    if 'deep.est.ai/volume-protection' in pvc.metadata.annotations and pvc.metadata.annotations['deep.est.ai/volume-protection'] == 'true':
        click.echo('cannot delete a volume. volume was protected.')
        return
    
    if not click.confirm('you really meant it?', default=False):
        click.echo('cancel deletation.')
        
    try:
        delete_persistent_volume_claim(
            name=name,
            namespace=namespace,
        )
        click.echo(f'volume "{name}" was deleted.')
    except NotFoundError as e:
        click.echo(f'volume "{name}" not found')
        exit(1)
