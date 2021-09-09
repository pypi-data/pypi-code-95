import pathlib
import click

path = pathlib.Path().resolve()

@click.command()
def test():
    with open(f"{path}/sample","a") as file:
        file.write("hello")

