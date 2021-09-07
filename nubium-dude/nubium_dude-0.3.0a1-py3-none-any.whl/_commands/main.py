from pathlib import Path
import runpy
import sys

import click

from .._utils import run_command_in_virtual_environment, sync_virtual_environment


@click.group(invoke_without_command=True)
@click.version_option(prog_name="dude")
@click.pass_context
def main(ctx):
    if ctx.invoked_subcommand is None:
        print_help()


@main.command()
def build_reqs():
    click.echo("TODO: run pip-compile")


@main.command("format")
def auto_format():
    sys.argv[1:] = ["."]
    runpy.run_module("black")


@main.command()
def lint():
    click.echo("TODO: run linter")


@main.command()
def test():
    # TODO ensure command is run from an app folder
    sync_virtual_environment()
    venv_path = Path("venv")
    run_command_in_virtual_environment(venv_path, "pytest")


def print_help():
    ctx = click.get_current_context()
    click.echo(ctx.get_help())
