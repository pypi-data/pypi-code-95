from kenna.api import Kenna

import click
import hodgepodge.types
import hodgepodge.click


@click.group()
@click.pass_context
def dashboard_groups(_):
    pass


@dashboard_groups.command()
@click.option('--dashboard-group-ids')
@click.option('--limit', default=None, type=int)
@click.pass_context
def count_dashboard_groups(ctx, dashboard_group_ids: str, limit: int):
    api = ctx.obj['kenna_api']
    assert isinstance(api, Kenna)

    rows = api.iter_dashboard_groups(
        dashboard_group_ids=hodgepodge.click.str_to_list_of_int(dashboard_group_ids),
        limit=limit,
    )
    count = sum(1 for _ in rows)
    click.echo(count)


@dashboard_groups.command()
@click.option('--dashboard-group-ids')
@click.option('--limit', default=None, type=int)
@click.pass_context
def get_dashboard_groups(ctx, dashboard_group_ids: str, limit: int):
    api = ctx.obj['kenna_api']
    assert isinstance(api, Kenna)

    for group in api.iter_dashboard_groups(
        dashboard_group_ids=hodgepodge.click.str_to_list_of_int(dashboard_group_ids),
        limit=limit,
    ):
        group = hodgepodge.types.dict_to_json(group)
        click.echo(group)


@dashboard_groups.command()
@click.option('--dashboard-group-id', required=True, type=int)
@click.pass_context
def get_dashboard_group(ctx, dashboard_group_id: int):
    api = ctx.obj['kenna_api']
    group = api.get_dashboard_group(dashboard_group_id=dashboard_group_id)
    if group:
        group = hodgepodge.types.dict_to_json(group)
        click.echo(group)
