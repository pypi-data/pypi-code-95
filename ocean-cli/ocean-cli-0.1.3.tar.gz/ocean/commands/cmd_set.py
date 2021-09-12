import click

from ocean import utils
from ocean.main import pass_env


@click.group(cls=utils.AliasedGroup)
def cli():
    pass


# Resources
@cli.command()
@click.argument("name")
@click.option("-d", "--default", is_flag=True, help="Set preset as default.")
@pass_env
def preset(ctx, name, default):
    if default:
        return ctx.set_presets_as_default(name)
