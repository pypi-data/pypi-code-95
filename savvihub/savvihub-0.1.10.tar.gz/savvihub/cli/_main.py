import os
import sys

project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
# this line should be on the top to run it on a local environment as 'python savvihub/cli/_main.py'
sys.path.append(project_root)

import click
import sentry_sdk
from click.decorators import pass_context
from sentry_sdk.integrations.logging import ignore_logger

import savvihub
from savvihub.cli._base import VesslGroup
from savvihub.cli._util import prompt_choices
from savvihub.cli.dataset import cli as dataset_cli
from savvihub.cli.experiment import cli as experiment_cli
from savvihub.cli.kernel_cluster import cli as kernel_cluster_cli
from savvihub.cli.kernel_image import cli as kernel_image_cli
from savvihub.cli.kernel_resource_spec import cli as kernel_resource_spec_cli
from savvihub.cli.model import cli as model_cli
from savvihub.cli.organization import cli as organization_cli
from savvihub.cli.project import cli as project_cli
from savvihub.cli.ssh_key import cli as ssh_key_cli
from savvihub.cli.sweep import cli as sweep_cli
from savvihub.cli.volume import cli as volume_cli
from savvihub.cli.workspace import cli as workspace_cli
from savvihub.util.config import DEFAULT_CONFIG_PATH, VesslConfigLoader
from savvihub.util.exception import (
    InvalidOrganizationError,
    InvalidProjectError,
    InvalidTokenError,
    SavvihubApiException,
)

# Configure Sentry
sentry_sdk.init(
    "https://e46fcd750b3a443fbd5b9dbc970e4ecf@o386227.ingest.sentry.io/5911639",
    traces_sample_rate=1.0,
)
ignore_logger("vessl_logger")


def prompt_organizations() -> str:
    organizations = savvihub.list_organizations()

    new_organization_string = "Create new organization..."
    choices = [x.name for x in organizations] + [new_organization_string]
    organization_name = prompt_choices("Default organization", choices)

    if organization_name == new_organization_string:
        organization_name = click.prompt("Organization name", type=click.STRING)
        regions = savvihub.vessl_api.region_list_api().regions
        region = prompt_choices("Region", [(x.name, x.value) for x in regions])
        savvihub.create_organization(organization_name, region)

    return organization_name


@click.command(cls=VesslGroup)
@click.version_option()
@pass_context
def cli(ctx: click.Context):
    savvihub.EXEC_MODE = "CLI"
    ctx.ensure_object(dict)


@cli.group(cls=VesslGroup, invoke_without_command=True)
@click.pass_context
@click.option("-t", "--access-token", type=click.STRING)
@click.option("-o", "--organization", type=click.STRING)
@click.option("-p", "--project", type=click.STRING)
@click.option("-f", "--credentials-file", type=click.STRING)
@click.option("--renew-token", is_flag=True)
def configure(
    ctx,
    access_token: str,
    organization: str,
    project: str,
    credentials_file: str,
    renew_token: bool,
):
    if ctx.invoked_subcommand:
        return

    try:
        savvihub.update_access_token(
            access_token=access_token,
            credentials_file=credentials_file,
            force_update=renew_token,
        )
    except InvalidTokenError:
        savvihub.update_access_token(force_update=True)

    try:
        savvihub.update_organization(
            organization_name=organization, credentials_file=credentials_file
        )
    except InvalidOrganizationError:
        organization_name = prompt_organizations()
        savvihub.update_organization(organization_name)

    try:
        savvihub.update_project(project_name=project, credentials_file=credentials_file)
    except InvalidProjectError:
        projects = savvihub.list_projects()
        if len(projects) == 0:
            return

        project_name = prompt_choices("Default project", [x.name for x in projects])
        savvihub.update_project(project_name)

    print(f"Welcome, {savvihub.vessl_api.user.display_name}!")


@configure.vessl_command()
@click.argument("organization", type=click.STRING, required=False)
def organization(organization: str):
    if organization is None:
        organization = prompt_organizations()
    savvihub.update_organization(organization)
    print(f"Saved to {DEFAULT_CONFIG_PATH}.")


@configure.vessl_command()
@click.argument("project", type=click.STRING, required=False)
def project(project: str):
    savvihub.vessl_api.set_organization()

    if project is None:
        projects = savvihub.list_projects()
        if len(projects) == 0:
            return

        project = prompt_choices("Default project", [x.name for x in projects])
    savvihub.update_project(project)
    print(f"Saved to {DEFAULT_CONFIG_PATH}.")


@configure.command()
def list():
    config = VesslConfigLoader()

    username = ""
    email = ""
    organization = config.default_organization or ""
    project = config.default_project or ""

    if config.access_token:
        savvihub.vessl_api.api_client.set_default_header(
            "Authorization", f"Token {config.access_token}"
        )

        try:
            user = savvihub.vessl_api.get_my_user_info_api()
            username = user.username
            email = user.email
        except SavvihubApiException as e:
            pass

    print(
        f"Username: {username}\n"
        f"Email: {email}\n"
        f"Organization: {organization}\n"
        f"Project: {project}"
    )


cli.add_command(dataset_cli)
cli.add_command(experiment_cli)
cli.add_command(kernel_cluster_cli)
cli.add_command(kernel_image_cli)
cli.add_command(kernel_resource_spec_cli)
cli.add_command(model_cli)
cli.add_command(organization_cli)
cli.add_command(project_cli)
cli.add_command(ssh_key_cli)
cli.add_command(sweep_cli)
cli.add_command(volume_cli)
cli.add_command(workspace_cli)


if __name__ == "__main__":
    cli()
