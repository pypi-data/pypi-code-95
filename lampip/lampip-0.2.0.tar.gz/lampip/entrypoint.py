import click

from . import __version__
from .core.workspace import Workspace


@click.group(help="Simple CLI tool for creating python custom lambda layers")
@click.version_option(__version__)
def main():
    pass


@main.command(help="Create the scaffold")
@click.argument("layer_name")
def new(layer_name: str):
    _ = Workspace.create_scaffold(layer_name)


@main.command(help="Build and push lambda layer")
@click.option("--upload/--no-upload", default=True)
def deploy(upload):
    ws = Workspace.load_directory(".")
    ws.deploy(upload_also=upload)
