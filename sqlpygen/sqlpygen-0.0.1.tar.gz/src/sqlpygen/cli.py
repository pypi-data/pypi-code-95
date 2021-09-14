"""Command line interface."""

import sys
from pathlib import Path

import click

from .sqlpygen import generate


@click.command()
@click.option(
    "-i",
    "--input",
    "input_file",
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
    required=True,
    help="Annotated sql file.",
)
@click.option(
    "-o",
    "--output",
    "output_file",
    type=click.Path(exists=False, file_okay=True, dir_okay=False),
    required=True,
    help="Generated python file.",
)
def cli(input_file, output_file):
    """SqlPyGen

    Generated type annotated python code from annotated SQL
    """
    input_file = Path(input_file)
    output_file = Path(output_file)

    input_ = input_file.read_text()
    try:
        output = generate(input_)
    except RuntimeError as e:
        click.secho(str(e), fg="red")
        sys.exit(1)

    output_file.write_text(output)
    click.secho("Python Code generated successfully", fg="green")
