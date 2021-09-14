#!/usr/bin/env python3
# type: ignore [misc]

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
from dotmap import DotMap
from pudb import set_trace as bp  # noqa: F401

from radiocc import NAME, VERSION, core, util
from radiocc.model import (
    Config,
    ConfigBuilder,
    ConfigKeysOpt,
    ConfigKeysReq,
    Folders,
)
from radiocc.util import (  # print_error,
    form_yes_or_no,
    format_error,
    print_info,
    print_validation,
    raise_error,
)

# MANIFEST_FILE = Path("pyproject.toml")
# MANIFEST = DotMap(envtoml.load(MANIFEST_FILE.open()))
# NAME = MANIFEST.tool.poetry.name
# VERSION = MANIFEST.tool.poetry.version

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])

FILE_PATH = Path(os.path.realpath(__file__))
SOURCES_PATH = FILE_PATH.parent
ASSETS_PATH = SOURCES_PATH / "assets"
CONFIG_PATH = ASSETS_PATH / "config.yaml"
DEFAULT_INFORMATION_PATH = ASSETS_PATH / Folders.information.name
DEFAULT_TO_PROCESS_PATH = Path(Folders.to_process.name)
DEFAULT_RESULTS_PATH = Path(Folders.results.name)
DEFAULT_CLI_STR = "\r"
DEFAULT_CLI_STR_FLAG = "\r\r"
REPLACEMENT_DEFAULT_CLI_STR_FLAG = None


def version(ctx: Any, param: Any, value: Any) -> None:
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
    callback=version,
    expose_value=False,
    is_eager=True,
    help="Show version.",
)
def cli(ctx: click.Context) -> None:
    """Radio occultations."""
    # Share default command options.
    ctx.ensure_object(dict)
    # ctx.obj["var"] = var

    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())
        ctx.exit()


@cli.command()
@click.option(
    "-g", "--gui", is_flag=True, help="Start the program with the graphical interface."
)
@click.pass_context
def run(
    ctx: click.Context,
    gui: bool,
) -> None:
    """Run the program."""
    run_gui() if gui else run_cli()


def run_cli() -> None:
    """Start the CLI program."""
    CFGF = read_config_file()
    CFG = parse_config_file(CFGF)
    check_config_folders_correct(CFG)

    core.initialization(CFG)


def run_gui() -> None:
    """Start the graphical interface."""
    CFGF = read_config_file()
    CFG = parse_config_file(CFGF)
    check_config_folders_correct(CFG)

    raise_error("the graphical interface is not implemented yet.")


@cli.command(name="config")
@click.pass_context
@click.option("--file", is_flag=True, help="Show the content of the config file.")
@click.option(
    "--information",
    is_flag=False,
    flag_value=DEFAULT_CLI_STR_FLAG,
    default=DEFAULT_CLI_STR,
    help="Set the path to the folder `information`.",
)
@click.option(
    "--to-process",
    "to_process",
    is_flag=False,
    flag_value=DEFAULT_CLI_STR_FLAG,
    default=DEFAULT_CLI_STR,
    help="Set the path to the folder `to_process`.",
)
@click.option(
    "--results",
    is_flag=False,
    flag_value=DEFAULT_CLI_STR_FLAG,
    default=DEFAULT_CLI_STR,
    help="Set the path to the folder `results`.",
)
@click.option(
    "--folders",
    is_flag=False,
    flag_value=DEFAULT_CLI_STR_FLAG,
    default=DEFAULT_CLI_STR,
    help="Set the path to the folders.",
)
def config_(
    ctx: click.Context,
    file: bool,
    information: str,
    to_process: str,
    results: str,
    folders: str,
) -> None:
    """Interact with the configurations."""
    # This function runs if no argument is not provided.
    config(ctx, file, information, to_process, results, folders)

    if file:
        config_file()
        return

    config_edit(information, to_process, results, folders)


def config(
    ctx: click.Context,
    file: str,
    information: str,
    to_process: str,
    results: str,
    folders: str,
) -> None:
    """Show the config formatted if no argument is provided."""
    if (
        not file
        and information == DEFAULT_CLI_STR
        and to_process == DEFAULT_CLI_STR
        and results == DEFAULT_CLI_STR
        and folders == DEFAULT_CLI_STR
    ):
        config_formatted()
        exit()


def config_file() -> None:
    """Show the config file."""
    CFGF = read_config_file()

    # Change all DEFAULT_CLI_STR_FLAG to None and all None to empty
    for (KEY, VALUE) in CFGF.items():
        if VALUE == DEFAULT_CLI_STR_FLAG or VALUE is None:
            CFGF[KEY] = ""

    print(f"Config file @{CONFIG_PATH}")
    print("\n".join(f"{attribute}: {value}" for (attribute, value) in CFGF.items()))

    CFG = parse_config_file(CFGF)
    check_config_folders_correct(CFG)


def config_formatted() -> None:
    """Show the config formatted."""
    CFGF = read_config_file()
    CFG = parse_config_file(CFGF)

    print("Configurations")
    print(str(CFG))

    check_config_folders_correct(CFG)


def config_edit(
    information: str = DEFAULT_CLI_STR,
    to_process: str = DEFAULT_CLI_STR,
    results: str = DEFAULT_CLI_STR,
    folders: str = DEFAULT_CLI_STR,
) -> None:
    """Edit the config file."""
    update = False
    CFGF = read_config_file()

    # Check if `information` variable has been asked to be changed.
    for (KEY, VALUE) in dict(
        information=information, to_process=to_process, results=results, folders=folders
    ).items():
        if VALUE != DEFAULT_CLI_STR:
            CFGF[KEY] = VALUE
            print_validation(
                f"CONFIG: the variable `{KEY}` has been changed to {VALUE}"
            )
            update = True

    # Change all DEFAULT_CLI_STR_FLAG to None and all None to empty
    for (KEY, VALUE) in CFGF.items():
        if VALUE == DEFAULT_CLI_STR_FLAG:
            CFGF[KEY] = None
    util.yaml_add_representer_none()

    # Update config file.
    if update:
        with open(CONFIG_PATH, "w") as fp:
            yaml.dump(CFGF.toDict(), fp)

    # Read config file again to check if it is correct.
    CFGF = read_config_file()
    CFG = parse_config_file(CFGF)
    check_config_folders_correct(CFG)


def config_information(information: str) -> None:
    """Edit the config information variable."""
    config_edit(information=information)


def config_to_process(to_process: str) -> None:
    """Edit the config to_process variable."""
    config_edit(to_process=to_process)


def config_results(results: str) -> None:
    """Edit the config results variable."""
    config_edit(results=results)


def config_folders(folders: str) -> None:
    """Edit the config folders variable."""
    config_edit(folders=folders)


def read_config_file() -> DotMap:
    """Load the config file."""
    CFGF_DICT, IND, BSI = ruamel.yaml.util.load_yaml_guess_indent(open(CONFIG_PATH))
    return DotMap(CFGF_DICT)


def parse_config_file(CFGF: DotMap) -> Config:
    """Check that the config file is correct."""
    # List the unused required variables.
    MISSING_VARIABLES = [KEY.name for KEY in list(ConfigKeysReq) if KEY not in CFGF]

    # Raise an error if any required variable is missing.
    if MISSING_VARIABLES:
        # as_list is true if at least two variables are missing, for plural syntax
        as_list = len(MISSING_VARIABLES) > 1
        raise_error(
            "the config file is missing the%s variable%s"
            % (("se", "s: ") if as_list else ("", ""))
            + ("\n- " if as_list else ": ").join([""] + MISSING_VARIABLES)
            + ("" if as_list else ".")
        )

    # Create the config object from its builder.
    cfg = ConfigBuilder()

    # Check if `folders` has been set.
    if ConfigKeysOpt.folders.name in CFGF:
        cfg.information = Path(CFGF.folders)
        cfg.to_process = Path(CFGF.folders)
        cfg.results = Path(CFGF.folders)

    # Check if information, to_process and results paths have been set.
    for KEY in list(Folders):
        if KEY.name in CFGF:
            VALUE = CFGF.get(KEY.name)
            setattr(cfg, KEY.name, Path(VALUE) if VALUE not in (None, "") else None)

    # Check the optional arguments that have not been set, to assign their default
    # values.
    # First check `information`.
    if cfg.information is None:
        cfg.information = DEFAULT_INFORMATION_PATH
        print_info(
            "`information` folder path unset: using the default `information` "
            "folder."
        )

    # Same check for `to_process`.
    if cfg.to_process is None:
        cfg.to_process = DEFAULT_TO_PROCESS_PATH
        print_info("`to_process` folder path unset: using the current path.")

    # Same check for `results`.
    if cfg.results is None:
        cfg.results = DEFAULT_RESULTS_PATH
        print_info("`results` folder path unset: using the current path.")

    return cfg.build()


def check_config_folders_correct(CFG: Config) -> None:
    """Check that the config folder paths are correct."""

    # Check that `information` folder is correct.
    if not CFG.information.is_dir():
        raise_error(
            f"`information` folder path: {CFG.information.resolve()} is not a "
            "directory"
        )

    # Check that `to_process` folder is correct.
    if not CFG.to_process.is_dir():
        raise_error(
            f"`to_process` folder path: {CFG.to_process.resolve()} is not a "
            "directory"
        )

    # Check that `results` folder is correct.
    if not CFG.results.is_dir():
        QUESTION = (
            format_error(
                f"`results` folder path: {CFG.results.resolve()} is not a directory.\n"
            )
            + "Do you want to create it?"
        )

        if form_yes_or_no(QUESTION):
            CFG.results.mkdir(parents=True)
            print_info("`results` folder created.")
        else:
            raise_error("You need to create a directory for the results.")


def main() -> None:
    cli(prog_name=NAME)


if __name__ == "__main__":
    main()
