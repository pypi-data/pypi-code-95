import click
from iictl.commands.volume.main import volume
from iictl.crud.persistent_volume_claim import patch_persistent_volume_claim
from iictl.utils.exception import NotFoundError

@volume.command()
@click.argument('name')
def unprotect(name):
    try:
        patch_persistent_volume_claim(
            name=name,
            namespace='notebook',
            body={'metadata':{'annotations':{'deep.est.ai/volume-protection': 'false'}}}
        )
    except NotFoundError as e:
        print(f'volume "{name}" not found')
        exit(1)

    
    print(f'A volume {name} was unprotected.')