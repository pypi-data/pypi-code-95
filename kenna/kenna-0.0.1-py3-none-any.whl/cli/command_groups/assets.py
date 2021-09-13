from kenna.api import Kenna

import click
import hodgepodge.types
import hodgepodge.click
import itertools
import json


@click.group()
@click.pass_context
def assets(_):
    pass


@assets.command()
@click.option('--asset-ids')
@click.option('--limit', default=None, type=int)
@click.pass_context
def count_assets(ctx, asset_ids: str, limit: int):
    api = ctx.obj['kenna_api']
    assert isinstance(api, Kenna)

    rows = api.iter_assets(asset_ids=hodgepodge.click.str_to_list_of_int(asset_ids), limit=limit)
    count = sum(1 for _ in rows)
    click.echo(count)


@assets.command()
@click.option('--asset-id', required=True, type=int)
@click.pass_context
def get_asset(ctx, asset_id: int):
    api = ctx.obj['kenna_api']
    assert isinstance(api, Kenna)

    row = api.get_asset(asset_id=asset_id)
    if row:
        row = hodgepodge.types.dict_to_json(row)
        click.echo(row)


@assets.command()
@click.option('--asset-ids')
@click.option('--limit', default=None, type=int)
@click.pass_context
def get_assets(ctx, asset_ids: str, limit: int):
    api = ctx.obj['kenna_api']
    assert isinstance(api, Kenna)

    for row in api.iter_assets(asset_ids=hodgepodge.click.str_to_list_of_int(asset_ids), limit=limit):
        row = hodgepodge.types.dict_to_json(row)
        click.echo(row)


@assets.command()
@click.option('--asset-ids')
@click.option('--limit', default=None, type=int)
@click.pass_context
def get_asset_tags(ctx, asset_ids: str, limit: int):
    api = ctx.obj['kenna_api']
    assert isinstance(api, Kenna)

    rows = api.iter_assets(
        asset_ids=hodgepodge.click.str_to_list_of_int(asset_ids),
        limit=limit,
    )
    tags = json.dumps(sorted(set(itertools.chain.from_iterable(row['tags'] for row in rows))))
    click.echo(tags)


@assets.command()
@click.option('--asset-ids')
@click.option('--limit', default=None, type=int)
@click.pass_context
def get_asset_hostnames(ctx, asset_ids: str, limit: int):
    api = ctx.obj['kenna_api']
    assert isinstance(api, Kenna)

    hostnames = set()
    for asset in api.iter_assets(asset_ids=hodgepodge.click.str_to_list_of_int(asset_ids), limit=limit):
        hostname = asset['hostname']
        if hostname:
            hostnames.add(hostname)

    hostnames = json.dumps(sorted(hostnames))
    click.echo(hostnames)


@assets.command()
@click.option('--asset-ids')
@click.option('--limit', default=None, type=int)
@click.pass_context
def get_asset_ipv4_addresses(ctx, asset_ids: str, limit: int):
    api = ctx.obj['kenna_api']
    assert isinstance(api, Kenna)

    ips = set()
    for asset in api.iter_assets(asset_ids=hodgepodge.click.str_to_list_of_int(asset_ids), limit=limit):
        ip = asset['ip_address']
        if ip:
            ips.add(ip)

    ips = json.dumps(sorted(ips))
    click.echo(ips)


@assets.command()
@click.option('--asset-ids')
@click.option('--limit', default=None, type=int)
@click.pass_context
def get_asset_ipv6_addresses(ctx, asset_ids: str, limit: int):
    api = ctx.obj['kenna_api']
    assert isinstance(api, Kenna)

    ips = set()
    for asset in api.iter_assets(asset_ids=hodgepodge.click.str_to_list_of_int(asset_ids), limit=limit):
        ip = asset['ipv6']
        if ip:
            ips.add(ip)

    ips = json.dumps(sorted(ips))
    click.echo(ips)
