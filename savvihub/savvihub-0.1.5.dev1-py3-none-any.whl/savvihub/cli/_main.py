import click
import sentry_sdk
from click.decorators import pass_context

import savvihub
from savvihub.cli._base import VesslGroup
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
from savvihub.util.config import VesslConfigLoader
from savvihub.util.exception import InvalidTokenError, SavvihubApiException

# Configure Sentry
sentry_sdk.init(
    "https://e46fcd750b3a443fbd5b9dbc970e4ecf@o386227.ingest.sentry.io/5911639",
    traces_sample_rate=1.0,
)


@click.command(cls=VesslGroup)
@click.version_option()
@pass_context
def cli(ctx: click.Context):
    ctx.ensure_object(dict)


access_token_option = click.option("-t", "--access-token", type=click.STRING)
organization_option = click.option("-o", "--organization", type=click.STRING)
project_option = click.option("-p", "--project", type=click.STRING)
credentials_file_option = click.option("-f", "--credentials-file", type=click.STRING)
force_update_option = click.option("--renew-token", is_flag=True)


def _login(access_token: str, credentials_file: str, renew_token: bool):
    try:
        savvihub.update_access_token(
            access_token=access_token,
            credentials_file=credentials_file,
            force_update=renew_token,
        )
    except InvalidTokenError:
        savvihub.update_access_token(force_update=True)
    print(f"Welcome, {savvihub.vessl_api.user.display_name}!")


@cli.command()
@access_token_option
@credentials_file_option
@force_update_option
def login(access_token: str, credentials_file: str, renew_token: bool):
    _login(access_token, credentials_file, renew_token)


@cli.command()
@access_token_option
@organization_option
@project_option
@credentials_file_option
@force_update_option
def init(access_token, organization, project, credentials_file, renew_token):
    _login(access_token, credentials_file, renew_token)

    savvihub.update_organization(
        organization_name=organization, credentials_file=credentials_file
    )

    if project is not None:
        savvihub.update_project(project_name=project, credentials_file=credentials_file)


@cli.command()
def status():
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
