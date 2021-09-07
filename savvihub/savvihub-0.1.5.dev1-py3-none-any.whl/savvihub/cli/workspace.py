import click

from savvihub.cli._base import VesslGroup, vessl_argument, vessl_option
from savvihub.cli._util import (
    Endpoint,
    format_string,
    generic_prompter,
    print_data,
    print_table,
    prompt_choices,
    truncate_datetime,
)
from savvihub.cli.organization import organization_name_option
from savvihub.util.constant import SSH_CONFIG_PATH
from savvihub.workspace import (
    backup_workspace,
    connect_workspace_ssh,
    list_workspaces,
    read_workspace,
    restore_workspace,
    update_vscode_remote_ssh,
)


def workspace_id_prompter(
    ctx: click.Context, param: click.Parameter, value: int
) -> int:
    workspaces = list_workspaces()
    return prompt_choices("Workspace", [(x.name, x.id) for x in workspaces])


@click.command(name="workspace", cls=VesslGroup)
def cli():
    pass


@cli.vessl_command()
@vessl_argument("id", type=click.INT, required=True, prompter=workspace_id_prompter)
@organization_name_option
def read(id: int):
    workspace = read_workspace(workspace_id=id)
    print_data(
        {
            "ID": workspace.id,
            "Name": workspace.name,
            "Status": workspace.status,
            "Creator": workspace.created_by.username,
            "Created": truncate_datetime(workspace.created_dt),
            "Cluster": workspace.kernel_cluster.name,
            "Root Volume Size": workspace.volume_mounts.root_volume_size,
            "Resource Spec": {
                "Name": workspace.kernel_resource_spec.name,
                "CPU": workspace.kernel_resource_spec.cpu_limit,
                "Memory": workspace.kernel_resource_spec.memory_limit,
                "GPU": f"{workspace.kernel_resource_spec.gpu_limit} ({workspace.kernel_resource_spec.gpu_type})",
            },
            "Ports": [
                {
                    "Name": x.name,
                    "Port": x.port,
                }
                for x in workspace.ports  # TODO: breaks if `nonprimitive_openapi_model_keys` is removed
            ],
            "SSH": format_string(workspace.endpoints.ssh),
        }
    )
    print(
        f"For more info: {Endpoint.workspace.format(workspace.organization.name, workspace.id)}"
    )


@cli.vessl_command()
@click.option("--cluster", type=click.INT, help="Filter workspaces by cluster ID.")
@click.option(
    "--status", type=click.STRING, multiple=True, help="Filter workspaces by status."
)
@click.option("--show-all", is_flag=True, help="If not set, only show my workspaces.")
@organization_name_option
def list(cluster: int, status: str, show_all: bool):
    workspaces = list_workspaces(
        cluster_id=cluster,
        statuses=status,
        mine=(not show_all),
    )
    print_table(
        workspaces,
        ["ID", "Name", "Status", "Creator", "Created", "Resource"],
        lambda x: [
            x.id,
            x.name,
            x.status,
            x.creator,
            truncate_datetime(x.created_dt),
            x.kernel_resource_spec.name,
        ],
    )


@cli.vessl_command()
def backup():
    backup_workspace()


@cli.vessl_command()
def restore():
    restore_workspace()


@cli.vessl_command()
@vessl_argument("id", type=click.INT, required=True, prompter=workspace_id_prompter)
@vessl_option(
    "-p",
    "--key-path",
    type=click.Path(exists=True),
    required=True,
    prompter=generic_prompter("Private key path"),
)
@organization_name_option
def ssh(id: int, key_path: str):
    connect_workspace_ssh(workspace_id=id, private_key_path=key_path)


@cli.vessl_command()
@vessl_option(
    "-p",
    "--key-path",
    type=click.Path(exists=True),
    required=True,
    prompter=generic_prompter("Private key path"),
)
def vscode(key_path: str):
    update_vscode_remote_ssh(private_key_path=key_path)
    print(f"Updated {SSH_CONFIG_PATH}.")
