import click
from iictl.commands.main import cli
from iictl.crud.integrated_instance import delete_integrated_instance
from iictl.utils.exception import NotFoundError

@cli.command()
@click.option('-f', '--force', is_flag=True)
@click.argument('name', nargs=-1)
def rm(name, force):
    if len(name) == 0:
            ctx = click.get_current_context()
            click.echo(ctx.get_help())
            
    for it in name:
        try:
            delete_integrated_instance(
                namespace='notebook',
                name=it
            )
        except NotFoundError as e:
            print(f'integrated instance "{it}" not found')
        else:
            print(f'integrated instance "{it}" deleted')
