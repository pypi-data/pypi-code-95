#!/usr/bin/env python3

"""
radiocc.
"""


import os
from pathlib import Path
from typing import Any

# import envtoml
import click
import ruamel.yaml
import yaml
from colored import attr, fg
from dotmap import DotMap
from pudb import set_trace as bp  # noqa: F401

from radiocc import NAME, VERSION, core
from radiocc.model import FoldersError

# MANIFEST_FILE = Path("pyproject.toml")
# MANIFEST = DotMap(envtoml.load(MANIFEST_FILE.open()))
# NAME = MANIFEST.tool.poetry.name
# VERSION = MANIFEST.tool.poetry.version

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])

FILE_PATH = Path(os.path.realpath(__file__))
CONFIG_PATH = FILE_PATH.parent / "config.yaml"


def print_version(ctx: Any, param: Any, value: Any) -> None:
    """Show version."""
    if not value or ctx.resilient_parsing:
        return
    click.echo(VERSION)
    ctx.exit()


@click.group(context_settings=CONTEXT_SETTINGS, invoke_without_command=True)
@click.pass_context
@click.option(
    "-v",
    "--version",
    is_flag=True,
    callback=print_version,
    expose_value=False,
    is_eager=True,
    help="Show version",
)
@click.option(
    "-g", "--gui", is_flag=True, help="start the program with the graphical interface"
)
def cli(ctx: click.Context, gui: bool) -> None:
    """Radio occultations."""
    if ctx.invoked_subcommand is None:
        # Start GUI if asked.
        if gui:
            core.gui()

        # Start the program with the given path.
        else:
            core.start()


@cli.command()
@click.pass_context
@click.option("-l", "--list", "list_", is_flag=True, help="list the configurations")
@click.option(
    "-p",
    "--path",
    type=str,
    default=" ",
    help="Set or get the path to the folders",
)
def config(ctx: click.Context, list_: bool, path: str) -> None:
    """Interact with the configurations"""
    update = False

    CONFIG_DICT, IND, BSI = ruamel.yaml.util.load_yaml_guess_indent(open(CONFIG_PATH))
    CONFIG = DotMap(CONFIG_DICT)

    if not list_ and path == " ":
        print(ctx.get_help())
        return

    if list_:
        core.check_folders_path_valid(CONFIG.folders_path)
        print(
            f"Path to the folders is {fg('green')}{Path(CONFIG.folders_path).resolve()}"
            f"{attr(0)}."
        )

    if path != " ":
        core.check_folders_path_valid(path, FoldersError.NotADir)
        CONFIG.folders_path = path
        print(
            "Path to the folders has been updated to "
            f"{fg('green')}{Path(path).resolve()}{attr(0)}!"
        )
        update = True

    # Update config file
    if update:
        with open(CONFIG_PATH, "w") as fp:
            yaml.dump(CONFIG.toDict(), fp)


def main() -> None:
    cli(prog_name=NAME)


if __name__ == "__main__":
    main()
