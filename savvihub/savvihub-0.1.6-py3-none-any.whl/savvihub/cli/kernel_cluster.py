import click

from savvihub.cli._base import VesslGroup, vessl_argument
from savvihub.cli._util import (
    format_string,
    generic_prompter,
    print_data,
    print_table,
    prompt_choices,
)
from savvihub.cli.organization import organization_name_option
from savvihub.kernel_cluster import (
    delete_cluster,
    list_cluster_nodes,
    list_clusters,
    read_cluster,
    rename_cluster,
)


def cluster_name_prompter(
    ctx: click.Context, param: click.Parameter, value: str
) -> str:
    clusters = list_clusters()
    return prompt_choices("Cluster", [x.name for x in clusters])


def custom_cluster_name_prompter(
    ctx: click.Context, param: click.Parameter, value: str
) -> str:
    clusters = list_clusters()
    clusters = [x for x in clusters if not x.is_savvihub_managed]
    return prompt_choices("Cluster", [x.name for x in clusters])


@click.command(name="cluster", cls=VesslGroup)
def cli():
    pass


@cli.vessl_command()
@vessl_argument(
    "name", type=click.STRING, required=True, prompter=cluster_name_prompter
)
@organization_name_option
def read(name: str):
    cluster = read_cluster(cluster_name=name)
    print_data(
        {
            "ID": cluster.id,
            "Name": cluster.name,
            "Type": "Managed" if cluster.is_savvihub_managed else "Custom",
            "Region": format_string(cluster.region),
            "Status": cluster.status.replace("-", " "),
            "K8s Master Endpoint": format_string(cluster.name),
            "K8s Namespace": format_string(cluster.kubernetes_namespace),
            "K8s Service Type": cluster.kubernetes_service_type,
        }
    )


@cli.vessl_command()
@organization_name_option
def list():
    clusters = list_clusters()
    print_table(
        clusters,
        ["ID", "Name", "Type", "Status", "K8s Master Endpoint", "K8s Namespace"],
        lambda x: [
            x.id,
            x.name,
            "Managed" if x.is_savvihub_managed else "Custom",
            x.status.replace("-", " "),
            format_string(x.name),
            format_string(x.kubernetes_namespace),
        ],
    )


@cli.vessl_command()
@vessl_argument(
    "name", type=click.STRING, required=True, prompter=custom_cluster_name_prompter
)
@organization_name_option
def delete(name: str):
    click.confirm(f"Are you sure you want to delete '{name}'?", abort=True)
    data = delete_cluster(cluster_name=name)
    print(f"Deleted '{name}'.")


@cli.vessl_command()
@vessl_argument(
    "name", type=click.STRING, required=True, prompter=custom_cluster_name_prompter
)
@vessl_argument(
    "new_name", type=click.STRING, required=True, prompter=generic_prompter("New name")
)
@organization_name_option
def rename(name: str, new_name: str):
    cluster = rename_cluster(cluster_name=name, new_cluster_name=new_name)
    print(f"Renamed '{name}' to '{cluster.name}'.")


@cli.vessl_command()
@vessl_argument(
    "name", type=click.STRING, required=True, prompter=custom_cluster_name_prompter
)
@organization_name_option
def list_nodes(name: str):
    cluster_nodes = list_cluster_nodes(cluster_name=name)
    print_table(
        cluster_nodes,
        ["ID", "Name", "CPU Limits", "GPU Limits", "Memory Limits"],
        lambda x: [x.id, x.name, x.cpu_limits, x.gpu_limits, x.memory_limits],
    )
