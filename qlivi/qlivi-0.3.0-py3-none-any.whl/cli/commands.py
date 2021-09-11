from typing import Any, Callable, Dict
import click

@click.command()
def init() -> None:
    """ Initialize A New Qlivi Project """

@click.command()
def info() -> None:
    """ Show Qlivi Project Info """

@click.command()
def run() -> None:
    """ Run Command From Qlivi Config File """

@click.command()
def test() -> None:
    """ Run Test Command From Qlivi Config File """

@click.command()
def setup() -> None:
    """ Run Setup Command From Qlivi Config File"""


commands: Dict[str, Callable[[], Any]] = {
    "run": run,
    "init": init,
    "info": info,
    "test": test,
    "setup": setup
}