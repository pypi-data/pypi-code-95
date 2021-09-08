import os

import click
from midas.tools import analysis
from midas.util.runtime_config import RuntimeConfig


def analyze(**kwargs):
    """The analyze function of midas CLI."""
    name = kwargs.get("db_file", None)
    if name is None:
        click.echo("No file provided. Terminating!")
        return

    if not name.endswith(".hdf5"):
        db_file = f"{name}.hdf5"
        name = os.path.split(name)[-1]
    else:
        db_file = name
        name = os.path.split(name)[-1][:-5]

    if not os.path.isfile(db_file):
        db_file = os.path.join(RuntimeConfig().paths["output_path"], db_file)

    if not os.path.isfile(db_file):
        click.echo(
            f"Could not find database at {kwargs.get('db_file')}. "
            "Terminating!"
        )
        return

    db_file = os.path.abspath(db_file)

    output_folder = kwargs.get("output_folder", None)
    if output_folder is None:
        output_folder = RuntimeConfig().paths["output_path"]

    output_folder = os.path.abspath(output_folder)
    if not output_folder.endswith(name):
        output_folder = os.path.join(output_folder, name)

    os.makedirs(output_folder, exist_ok=True)

    click.echo(f'Reading database at "{db_file}".')
    click.echo(f'Saving results to "{output_folder}".')

    analysis.analyze(
        name, db_file, output_folder, kwargs.get("db_style", "mosaik")
    )
