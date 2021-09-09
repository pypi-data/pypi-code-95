import click
from .midhash import run
from .pare_xml import parse_xml_folder
import sys
from .Scraper import main

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


def echo_midhash(ctx, params, value):
    if value is not None:
        click.echo(run(value))
        ctx.exit()


def echo_version(ctx, param, value):
    if value:
        click.echo('0.0.1')
        ctx.exit()


def verv_folder(ctx, params, value):
    if value is not None:
        parse_xml_folder(value)
        ctx.exit()


def set_sessdata(ctx, params, value):
    if value is not None:
        src = sys.path[4]
        with open('%s\\data.txt' % src, 'w', encoding='utf-8') as f:
            f.write(value)
        ctx.exit()


@click.group(context_settings=CONTEXT_SETTINGS)
@click.option('-v', '--version', is_flag=True, callback=echo_version,
              expose_value=False, is_eager=True)
@click.option('-m', '--midhash', callback=echo_midhash, type=str,
              expose_value=False)
@click.option('-f', '--folder', callback=verv_folder, type=str,
              expose_value=False)
@click.option('-s', '--sessdata', callback=set_sessdata, type=str,
              expose_value=False)
def cli():
    pass


@cli.command()
@click.option('-s', '--startday')
@click.option('-e', '--endday')
@click.option('-o', '--oid', type=int)
@click.option('-t', '--time', type=int, required=False, default=1)
def history(startday, endday, oid, time):
    main(startday, endday, oid, time)


if __name__ == '__main__':
    cli()
