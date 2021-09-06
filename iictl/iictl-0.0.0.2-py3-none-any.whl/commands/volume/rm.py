import click
from iictl.commands.volume.main import volume
from iictl.crud.persistent_volume_claim import read_persistent_volume_claim
from iictl.crud.persistent_volume_claim import delete_persistent_volume_claim
from iictl.utils.exception import NotFoundError

@volume.command() #really meant it?()
@click.argument('name')
def rm(name):
    try:
        pvc = read_persistent_volume_claim(
            name=name,
            namespace='notebook',
        )
    except NotFoundError as e:
        print(f'volume "{name}" not found')
        exit(1)
    
    if 'deep.est.ai/volume-protection' in pvc.metadata.annotations and pvc.metadata.annotations['deep.est.ai/volume-protection'] == 'true':
        print('cannot delete a volume. volume was protected.')
        return
    
    if not click.confirm('you really meant it?', default=False):
        print('cancel deletation.')
        
    try:
        delete_persistent_volume_claim(
            name=name,
            namespace='notebook',
        )
        print(f'A volume {name} was deleted.')
    except NotFounderror as e:
        print(f'volume "{name}" not found')
        exit(1)
