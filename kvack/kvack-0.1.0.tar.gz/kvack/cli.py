"""Console script for kvack."""
import sys
from typing import Any, cast

import click
import toml

ConfigType = dict[str, dict[str, dict[str, dict[str, dict[str, Any]]]]]  # type: ignore


@click.group()  # type: ignore
def main() -> None:
    pass


@main.command()  # type: ignore
def gen() -> None:
    config = cast(ConfigType, toml.load("pyproject.toml"))
    tools = config["tool"]["kvack"]["tool"]
    for name, options in tools.items():
        config["tool"].setdefault(name, {}).update(options)
    with open("pyproject.toml", "w+") as pyproject_file:
        toml.dump(config, pyproject_file)
    click.echo(f"Tool configs generated: {', '.join(tools)}")


if __name__ == "__main__":
    sys.exit(main())  # type: ignore
