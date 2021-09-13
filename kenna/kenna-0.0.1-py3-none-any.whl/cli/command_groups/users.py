from kenna.api import Kenna

import click
import hodgepodge.types
import hodgepodge.click


@click.group()
@click.pass_context
def users(_):
    pass


@users.command()
@click.option('--user-ids')
@click.option('--limit', default=None, type=int)
@click.pass_context
def count_users(ctx, user_ids: str, limit: int):
    api = ctx.obj['kenna_api']
    assert isinstance(api, Kenna)

    rows = api.iter_users(
        user_ids=hodgepodge.click.str_to_list_of_int(user_ids),
        limit=limit,
    )
    count = sum(1 for _ in rows)
    click.echo(count)


@users.command()
@click.option('--user-ids')
@click.option('--limit', default=None, type=int)
@click.pass_context
def get_users(ctx, user_ids: str, limit: int):
    api = ctx.obj['kenna_api']
    assert isinstance(api, Kenna)

    for user in api.iter_users(
        user_ids=hodgepodge.click.str_to_list_of_int(user_ids),
        limit=limit,
    ):
        user = hodgepodge.types.dict_to_json(user)
        click.echo(user)


@users.command()
@click.option('--user-ids')
@click.option('--limit', default=None, type=int)
@click.pass_context
def get_users(ctx, user_ids: str, limit: int):
    api = ctx.obj['kenna_api']
    assert isinstance(api, Kenna)

    for user in api.iter_users(
        user_ids=hodgepodge.click.str_to_list_of_int(user_ids),
        limit=limit,
    ):
        user = hodgepodge.types.dict_to_json(user)
        click.echo(user)


@users.command()
@click.option('--user-id', required=True, type=int)
@click.pass_context
def get_user(ctx, user_id: int):
    api = ctx.obj['kenna_api']
    assert isinstance(api, Kenna)

    user = api.get_user(user_id=user_id)
    if user:
        user = hodgepodge.types.dict_to_json(user)
        click.echo(user)
