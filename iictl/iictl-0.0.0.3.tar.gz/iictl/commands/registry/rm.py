import click
from iictl.commands.registry.main import registry
from iictl.crud.secret import read_secret
from iictl.crud.secret import delete_secret
from iictl.utils.exception import NotFoundError
from iictl.utils.click import global_option

@registry.command(help='remove registry') #really meant it?()
@click.option('-n', '--namespace', type=str, help='name of namespace', callback=global_option)
@click.argument('name')
def rm(name, namespace):
    try:
        delete_secret(
            name=name,
            namespace=namespace,
        )
        click.echo(f'secret "{name}" was deleted.')
    except NotFoundError as e:
        click.echo(f'secret "{name}" not found')
        exit(1)
