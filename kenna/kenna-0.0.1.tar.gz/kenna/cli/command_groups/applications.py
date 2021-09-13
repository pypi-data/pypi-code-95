from kenna.api import Kenna

import click
import hodgepodge.types
import hodgepodge.click
import json


@click.group()
@click.pass_context
def applications(_):
    pass


@applications.command()
@click.option('--application-ids')
@click.option('--limit', default=None, type=int)
@click.pass_context
def count_applications(ctx, application_ids: str, limit: int):
    api = ctx.obj['kenna_api']
    assert isinstance(api, Kenna)

    rows = api.iter_applications(application_ids=hodgepodge.click.str_to_list_of_int(application_ids), limit=limit)
    count = sum(1 for _ in rows)
    click.echo(count)


@applications.command()
@click.option('--application-id', required=True, type=int)
@click.pass_context
def get_application(ctx, application_id: int):
    api = ctx.obj['kenna_api']
    assert isinstance(api, Kenna)

    row = api.get_application(application_id=application_id)
    if row:
        row = hodgepodge.types.dict_to_json(row)
        click.echo(row)


@applications.command()
@click.option('--application-ids')
@click.option('--limit', default=None, type=int)
@click.pass_context
def get_applications(ctx, application_ids: str, limit: int):
    api = ctx.obj['kenna_api']
    assert isinstance(api, Kenna)

    for row in api.iter_applications(application_ids=hodgepodge.click.str_to_list_of_int(application_ids), limit=limit):
        row = hodgepodge.types.dict_to_json(row)
        click.echo(row)


@applications.command()
@click.option('--application-ids')
@click.option('--limit', default=None, type=int)
@click.pass_context
def get_application_ids(ctx, application_ids: str, limit: int):
    api = ctx.obj['kenna_api']
    assert isinstance(api, Kenna)

    rows = api.iter_applications(application_ids=hodgepodge.click.str_to_list_of_int(application_ids), limit=limit)
    ids = set(filter(bool, [app['id'] for app in rows]))
    txt = json.dumps(sorted(ids))
    click.echo(txt)


@applications.command()
@click.option('--application-ids')
@click.option('--limit', default=None, type=int)
@click.pass_context
def get_application_names(ctx, application_ids: str, limit: int):
    api = ctx.obj['kenna_api']
    assert isinstance(api, Kenna)

    apps = api.iter_applications(application_ids=hodgepodge.click.str_to_list_of_int(application_ids), limit=limit)
    names = set(filter(bool, [app['name'] for app in apps]))
    txt = json.dumps(sorted(names))
    click.echo(txt)


@applications.command()
@click.option('--application-ids')
@click.option('--limit', default=None, type=int)
@click.pass_context
def get_application_owners(ctx, application_ids: str, limit: int):
    api = ctx.obj['kenna_api']
    assert isinstance(api, Kenna)

    apps = api.iter_applications(application_ids=hodgepodge.click.str_to_list_of_int(application_ids), limit=limit)
    owners = set(filter(bool, [app['owner'] for app in apps]))
    txt = json.dumps(sorted(owners))
    click.echo(txt)
