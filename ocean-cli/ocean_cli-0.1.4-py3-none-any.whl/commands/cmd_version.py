import click

from ocean import code


@click.command()
def cli():
    print(code.VERSION)
