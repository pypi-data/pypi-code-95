import pathlib
import click
import json

path = pathlib.Path().resolve()

@click.command()
def test():
    # with open(f"{path}/sample.txt","a") as file:
    #     file.write("hello")

    with open("info.txt") as file:
        # info1 = json.load(file)
        info = file.readlines()
        data = json.load(info)
        print(data)
        # print(info1) 

