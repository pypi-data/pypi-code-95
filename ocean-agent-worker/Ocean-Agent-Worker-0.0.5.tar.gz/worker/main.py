import logging

import click

from worker.cmd.hello import hello as worker_hello
from worker.cmd.join import join as worker_join
from worker.cmd.serve import serve as worker_serve

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')


@click.group()
def cli():
    pass


@cli.command()
@click.option("--master-endpoint", help="Endpoint of master agent endpoint.", type=click.STRING, required=True)
def hello(master_endpoint):
    worker_hello(master_endpoint)


@cli.command()
@click.option("--master-endpoint", help="Endpoint of master agent endpoint", type=click.STRING, required=True)
def join(master_endpoint):
    worker_join(master_endpoint)


@cli.command()
def serve():
    worker_serve()


if __name__ == "__main__":
    cli()
