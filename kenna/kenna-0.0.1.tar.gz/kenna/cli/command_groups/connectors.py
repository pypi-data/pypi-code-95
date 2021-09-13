from kenna.api import Kenna

import click
import hodgepodge.types
import hodgepodge.click


@click.group()
@click.pass_context
def connectors(_):
    pass


@connectors.command()
@click.option('--connector-ids')
@click.option('--limit', default=None, type=int)
@click.pass_context
def count_connectors(ctx, connector_ids: str, limit: int):
    api = ctx.obj['kenna_api']
    assert isinstance(api, Kenna)

    rows = api.iter_connectors(connector_ids=hodgepodge.click.str_to_list_of_int(connector_ids), limit=limit)
    count = sum(1 for _ in rows)
    click.echo(count)


@connectors.command()
@click.option('--connector-ids')
@click.option('--limit', default=None, type=int)
@click.pass_context
def get_connectors(ctx, connector_ids: str, limit: int):
    api = ctx.obj['kenna_api']
    for row in api.iter_connectors(
        connector_ids=hodgepodge.click.str_to_list_of_int(connector_ids),
        limit=limit,
    ):
        row = hodgepodge.types.dict_to_json(row)
        click.echo(row)


@connectors.command()
@click.option('--connector-id', required=True, type=int)
@click.pass_context
def get_connector(ctx, connector_id: int):
    api = ctx.obj['kenna_api']
    row = api.get_connector(connector_id=connector_id)
    if row:
        row = hodgepodge.types.dict_to_json(row)
        click.echo(row)


@connectors.command()
@click.option('--connector-ids')
@click.option('--connector-run-ids')
@click.option('--limit', default=None, type=int)
@click.pass_context
def get_connector_runs(ctx, connector_ids: str, connector_run_ids: str, limit: int):
    api = ctx.obj['kenna_api']
    assert isinstance(api, Kenna)

    for run in api.iter_connector_runs(
        connector_ids=hodgepodge.click.str_to_list_of_int(connector_ids),
        connector_run_ids=hodgepodge.click.str_to_list_of_int(connector_run_ids),
        limit=limit,
    ):
        run = hodgepodge.types.dict_to_json(run)
        click.echo(run)


@connectors.command()
@click.option('--connector-run', type=int)
@click.option('--connector-run-id', type=int)
@click.pass_context
def get_connector_run(ctx, connector_id: int, connector_run_id: int):
    api = ctx.obj['kenna_api']
    assert isinstance(api, Kenna)

    run = api.get_connector_run(
        connector_id=connector_id,
        connector_run_id=connector_run_id,
    )
    if run:
        run = hodgepodge.types.dict_to_json(run)
        click.echo(run)
