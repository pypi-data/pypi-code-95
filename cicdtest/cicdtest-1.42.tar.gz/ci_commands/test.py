import pathlib
import click
import json

path = pathlib.Path().resolve()

@click.command()
def test():
    # with open(f"{path}/sample.txt","a") as file:
    #     file.write("hello")

    with open("/home/kush/cron_test/buildpan_test/info.txt") as file:
        info = file.readlines()
        print(info)
        for data in info:
            d = eval(data)
            print(d)

