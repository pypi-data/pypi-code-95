import json
from pathlib import Path

import rich
from octadocs.cli.sparql import create_octiron
from typer import Typer

app = Typer(name='context')


@app.callback(invoke_without_command=True)
def context(path: Path):
    """Print context for a path."""
    octiron = create_octiron()
    ctx = octiron.get_context_per_directory(path)
    rich.print(json.dumps(
        ctx,
        indent=2,
        ensure_ascii=False,
    ))
