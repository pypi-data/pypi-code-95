import click

import savvihub
from savvihub.cli._base import VesslGroup, vessl_argument
from savvihub.cli._util import (
    Endpoint,
    generic_prompter,
    print_data,
    print_table,
    prompt_choices,
)
from savvihub.organization import (
    create_organization,
    list_organizations,
    read_organization,
)


def organization_name_prompter(
    ctx: click.Context, param: click.Parameter, value: str
) -> str:
    organizations = list_organizations()
    return prompt_choices("Organization", [x.name for x in organizations])


def region_prompter(ctx: click.Context, param: click.Parameter, value: str) -> str:
    regions = savvihub.vessl_api.region_list_api().regions
    return prompt_choices("Region", [(x.name, x.value) for x in regions])


@click.command(name="organization", cls=VesslGroup)
def cli():
    pass


@cli.vessl_command()
@vessl_argument(
    "name",
    type=click.STRING,
    required=True,
    prompter=organization_name_prompter,
)
def read(name: str):
    organization = read_organization(organization_name=name)
    print_data(
        {
            "ID": organization.id,
            "Name": organization.name,
            "Region": organization.default_region,
            "Description": organization.description,
        }
    )


@cli.vessl_command()
def list():
    organizations = list_organizations()
    print_table(
        organizations,
        ["ID", "Name", "Region"],
        lambda x: [x.id, x.name, x.default_region],
    )


@cli.vessl_command()
@vessl_argument(
    "name",
    type=click.STRING,
    required=True,
    prompter=generic_prompter("Organization name"),
)
@vessl_argument("region", type=click.STRING, required=True, prompter=region_prompter)
def create(name: str, region: str):
    organization = create_organization(organization_name=name, region=region)
    print(
        f"Created '{organization.name}'.\n"
        f"For more info: {Endpoint.organization.format(organization.name)}"
    )


# Ensure this is called before other options with `is_eager=True` for
# other callbacks that need organization to be preconfigured.
organization_name_option = click.option(
    "--organization",
    "organization_name",
    type=click.STRING,
    hidden=True,
    is_eager=True,
    expose_value=False,
    callback=lambda ctx, param, value: savvihub.vessl_api.set_organization(value),
    help="Override default organization.",
)
