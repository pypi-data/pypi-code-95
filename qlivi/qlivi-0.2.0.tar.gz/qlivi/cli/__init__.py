import click
from qlivi.cli.commands import commands

@click.group()
def cli() -> None:
    """ Qlivi Command Line Interface"""

for command in commands:
    cli.add_command(commands[command], command)