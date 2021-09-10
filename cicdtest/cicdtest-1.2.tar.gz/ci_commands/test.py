import pathlib
import click

path = pathlib.Path().resolve()

@click.command()
def test():
    with open(f"sample.txt","a") as file:
        file.write("hello")

