import click
from iictl.commands.volume.main import volume
from iictl.crud.persistent_volume_claim import create_persistent_volume_claim
from iictl.utils.exception import AlreadyExistError

@volume.command()
@click.argument('name')
@click.argument('size')
def create(name, size):
    try:
        create_persistent_volume_claim(
            name=name,
            namespace='notebook',
            size=size,
        )
        print(f'A volume "{name}" creation was requested.')
    except AlreadyExistError as e:
        print(f'A volume "{name}" already exist')
