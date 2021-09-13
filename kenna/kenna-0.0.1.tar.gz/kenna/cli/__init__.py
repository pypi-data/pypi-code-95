import click

from kenna import DEFAULT_API_KEY
from kenna.api import Kenna
from kenna.cli.command_groups.applications import applications
from kenna.cli.command_groups.assets import assets
from kenna.cli.command_groups.connectors import connectors
from kenna.cli.command_groups.dashboard_groups import dashboard_groups
from kenna.cli.command_groups.fixes import fixes
from kenna.cli.command_groups.roles import roles
from kenna.cli.command_groups.users import users
from kenna.cli.command_groups.vulnerabilities import vulnerabilities
from kenna.region import DEFAULT_REGION


@click.group()
@click.option('--api-key', default=DEFAULT_API_KEY)
@click.option('--region', default=DEFAULT_REGION)
@click.pass_context
def cli(ctx, api_key, region):
    ctx.ensure_object(dict)
    ctx.obj['kenna_api'] = Kenna(api_key=api_key, region=region)


COMMAND_GROUPS = [
    applications,
    assets,
    connectors,
    dashboard_groups,
    fixes,
    roles,
    users,
    vulnerabilities,
]
for command_group in COMMAND_GROUPS:
    cli.add_command(command_group)
