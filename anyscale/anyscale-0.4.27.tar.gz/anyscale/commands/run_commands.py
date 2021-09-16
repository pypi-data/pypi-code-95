from typing import List

import click

from anyscale.background import run


@click.command(
    name="run",
    help="Run a shell command as a background job on anyscale. This command is currently experimental.",
)
@click.option(
    "--env",
    required=False,
    type=click.Path(exists=True),
    help="File to load the runtime environment from. Accepts YAML or JSON format",
)
@click.argument("commands", nargs=-1, type=str)
def anyscale_run(env: str, commands: List[str],) -> None:
    manager = run(" ".join(commands), runtime_env=env)
    manager.wait()
