# type: ignore[attr-defined]
from typing import Optional

from enum import Enum
from random import choice

import typer
from rich.console import Console

from snowflakeio import version
from snowflakeio.sample import generate_sample_data


class Color(str, Enum):
    white = "white"
    red = "red"
    cyan = "cyan"
    magenta = "magenta"
    yellow = "yellow"
    green = "green"


app = typer.Typer(
    name="snowflakeio",
    help="Snowflake IO, a Pythonic Algorithmic Trading Library",
    add_completion=False,
)
console = Console()


def version_callback(print_version: bool) -> None:
    """Print the version of the package."""
    if print_version:
        console.print(f"[yellow]snowflakeio[/] version: [bold blue]{version}[/]")
        raise typer.Exit()


@app.command(name="")
def main(
    ticker: str = typer.Option(..., help="The stock symbol to run the program against"),
    color: Optional[Color] = typer.Option(
        None,
        "-c",
        "--color",
        "--colour",
        case_sensitive=False,
        help="Color for print. If not specified then choice will be random.",
    ),
    print_version: bool = typer.Option(
        None,
        "-v",
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Prints the version of the snowflakeio package.",
    ),
) -> None:
    """Print a greeting with a giving name."""
    if color is None:
        color = choice(list(Color))

    console.print(f"[bold {color}]{generate_sample_data(5, 3, 'D')}[/]")


if __name__ == "__main__":
    app()
