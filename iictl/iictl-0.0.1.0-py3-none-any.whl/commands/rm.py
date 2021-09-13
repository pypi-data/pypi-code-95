import click
from iictl.commands.main import cli
from iictl.crud.integrated_instance import delete_integrated_instance
from iictl.utils.exception import NotFoundError
from iictl.utils.click import global_option
from iictl.utils.parse import verify_object_name

@cli.command(help='remove instance')
@click.option('-f', '--force', is_flag=True)
@click.option('-n', '--namespace', type=str, help='name of namespace', callback=global_option)
@click.argument('name', nargs=-1)
def rm(name, force, namespace):
    if not verify_object_name(name):
        click.echo('wrong object name')
        return 
    
    if len(name) == 0:
            ctx = click.get_current_context()
            click.echo(ctx.get_help())
            
    for it in name:
        try:
            delete_integrated_instance(
                namespace=namespace,
                name=it
            )
        except NotFoundError as e:
            click.echo(f'integrated instance "{it}" not found')
        else:
            click.echo(f'integrated instance "{it}" deleted')
