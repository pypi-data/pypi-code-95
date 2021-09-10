import pathlib
import click

path = pathlib.Path().resolve()

@click.command()
def test():
    with open("sample.txt","a") as file:
        file.write("hello")

