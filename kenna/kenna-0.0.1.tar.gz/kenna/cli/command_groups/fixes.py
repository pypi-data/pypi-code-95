from kenna.api import Kenna

import click
import hodgepodge.types
import hodgepodge.click


@click.group()
@click.pass_context
def fixes(_):
    pass


@fixes.command()
@click.option('--fix-ids')
@click.option('--limit', default=None, type=int)
@click.pass_context
def count_fixes(ctx, fix_ids: str, limit: int):
    api = ctx.obj['kenna_api']
    assert isinstance(api, Kenna)

    rows = api.iter_fixes(
        fix_ids=hodgepodge.click.str_to_list_of_int(fix_ids),
        limit=limit,
    )
    count = sum(1 for _ in rows)
    click.echo(count)


@fixes.command()
@click.option('--fix-ids')
@click.option('--limit', default=None, type=int)
@click.pass_context
def get_fixes(ctx, fix_ids: str, limit: int):
    api = ctx.obj['kenna_api']
    assert isinstance(api, Kenna)

    for fix in api.iter_fixes(
        fix_ids=hodgepodge.click.str_to_list_of_int(fix_ids),
        limit=limit,
    ):
        fix = hodgepodge.types.dict_to_json(fix)
        click.echo(fix)


@fixes.command()
@click.option('--fix-id', required=True, type=int)
@click.pass_context
def get_fix(ctx, fix_id: int):
    api = ctx.obj['kenna_api']
    assert isinstance(api, Kenna)

    fix = api.get_fix(fix_id=fix_id)
    if fix:
        fix = hodgepodge.types.dict_to_json(fix)
        click.echo(fix)
