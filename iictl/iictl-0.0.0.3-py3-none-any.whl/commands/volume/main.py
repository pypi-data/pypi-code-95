import click
from iictl.commands import cli
from iictl.utils.click import global_option

@cli.group()
@click.pass_context
@click.option('-n', '--namespace', type=str, help='name of namespace', callback=global_option)
def volume(ctx, namespace):
    pass
