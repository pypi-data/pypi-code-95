import click
import hodgepodge.types
import hodgepodge.click
from kenna.api import Kenna


@click.group()
@click.pass_context
def roles(_):
    pass


@roles.command()
@click.option('--role-ids')
@click.option('--limit', default=None, type=int)
@click.pass_context
def count_roles(ctx, role_ids: str, limit: int):
    api = ctx.obj['kenna_api']
    assert isinstance(api, Kenna)

    rows = api.iter_roles(
        role_ids=hodgepodge.click.str_to_list_of_int(role_ids),
        limit=limit,
    )
    count = sum(1 for _ in rows)
    click.echo(count)


@roles.command()
@click.option('--role-ids')
@click.option('--limit', default=None, type=int)
@click.pass_context
def get_roles(ctx, role_ids: str, limit: int):
    api = ctx.obj['kenna_api']
    assert isinstance(api, Kenna)

    for role in api.iter_roles(
        role_ids=hodgepodge.click.str_to_list_of_int(role_ids),
        limit=limit,
    ):
        role = hodgepodge.types.dict_to_json(role)
        click.echo(role)


@roles.command()
@click.option('--role-id', required=True, type=int)
@click.pass_context
def get_role(ctx, role_id: int):
    api = ctx.obj['kenna_api']
    assert isinstance(api, Kenna)

    role = api.get_role(role_id=role_id)
    if role:
        role = hodgepodge.types.dict_to_json(role)
        click.echo(role)
