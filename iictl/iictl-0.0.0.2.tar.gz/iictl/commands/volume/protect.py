import click
from iictl.commands.volume.main import volume
from iictl.crud.persistent_volume_claim import patch_persistent_volume_claim
from iictl.utils.exception import NotFoundError

@volume.command()
@click.argument('name')
def protect(name):
    try:
        patch_persistent_volume_claim(
            name=name,
            namespace='notebook',
            body={'metadata':{'annotations':{'deep.est.ai/volume-protection': 'true'}}}
        )

        print(f'A volume {name} was protected.')
    except NotFoundError as e:
        print(f'volume "{name}" not found')