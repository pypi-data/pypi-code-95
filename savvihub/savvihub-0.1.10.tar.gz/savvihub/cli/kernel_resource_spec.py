import click

from savvihub.cli._base import VesslGroup, vessl_argument
from savvihub.cli._util import format_bool, print_data, print_table, prompt_choices
from savvihub.cli.organization import organization_name_option
from savvihub.kernel_resource_spec import (
    list_kernel_resource_specs,
    read_kernel_resource_spec,
)


def resource_name_prompter(
    ctx: click.Context, param: click.Parameter, value: str
) -> str:
    resources = list_kernel_resource_specs()
    return prompt_choices("Resource", [x.name for x in resources])


@click.command(name="resource", cls=VesslGroup)
def cli():
    pass


@cli.vessl_command()
@vessl_argument(
    "name", type=click.STRING, required=True, prompter=resource_name_prompter
)
@organization_name_option
def read(name: str):
    resource = read_kernel_resource_spec(kernel_resource_spec_name=name)
    print_data(
        {
            "ID": resource.id,
            "Name": resource.name,
            "Description": resource.description,
            "CPU Type": resource.cpu_type,
            "CPU Limit": resource.cpu_limit,
            "GPU Type": resource.gpu_type,
            "GPU Limit": resource.gpu_limit,
            "Memory Limit": resource.memory_limit,
            "Spot": format_bool(resource.spot),
            "Region": resource.region,
        }
    )


@cli.vessl_command()
@organization_name_option
def list():
    resources = list_kernel_resource_specs()
    print_table(
        resources,
        [
            "ID",
            "Name",
            "CPU Type",
            "CPU Limit",
            "GPU Type",
            "GPU Limit",
            "Memory Limit",
            "Spot",
        ],
        lambda x: [
            x.id,
            x.name,
            x.cpu_type,
            x.cpu_limit,
            x.gpu_type,
            x.gpu_limit,
            x.memory_limit,
            x.spot,
        ],
    )
