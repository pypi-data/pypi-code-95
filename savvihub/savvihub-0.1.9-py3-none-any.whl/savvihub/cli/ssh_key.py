import click

from savvihub.cli._base import VesslGroup, vessl_argument
from savvihub.cli._util import (
    generic_prompter,
    print_table,
    prompt_choices,
    truncate_datetime,
)
from savvihub.ssh_key import create_ssh_key, delete_ssh_key, list_ssh_keys


def ssh_key_id_prompter(ctx: click.Context, param: click.Parameter, value: int) -> int:
    ssh_keys = list_ssh_keys()
    return prompt_choices(
        "SSH key", [(f"{x.name} ({x.created_dt})", x.id) for x in ssh_keys]
    )


@click.command(name="ssh-key", cls=VesslGroup)
def cli():
    pass


@cli.vessl_command()
def list():
    ssh_keys = list_ssh_keys()
    print_table(
        ssh_keys,
        ["ID", "Name", "File", "Created"],
        lambda x: [x.id, x.name, x.filename, truncate_datetime(x.created_dt)],
    )


@cli.vessl_command()
@vessl_argument(
    "name", type=click.STRING, required=True, prompter=generic_prompter("SSH key name")
)
@vessl_argument(
    "path",
    type=click.Path(exists=True),
    required=True,
    prompter=generic_prompter("Path to public key"),
)
def create(name: str, path: str):
    ssh_key = create_ssh_key(key_name=name, key_path=path)
    print(f"SSH Key '{ssh_key.name}' created.")


@cli.vessl_command()
@vessl_argument("id", type=click.INT, required=True, prompter=ssh_key_id_prompter)
def delete(id: int):
    data = delete_ssh_key(key_id=id)
    print(f"Deleted {id}.")
