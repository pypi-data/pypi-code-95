import pathlib
import click
import json

path = pathlib.Path().resolve()

@click.command()
def test():
    # with open(f"{path}/sample.txt","a") as file:
    #     file.write("hello")

    with open("info.txt") as file:
        info = file.readlines()
        
        for data in info:
            data = eval(data)
            print(data)

