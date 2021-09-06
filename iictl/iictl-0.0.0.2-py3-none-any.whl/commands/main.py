import click
from kubernetes import client, config
@click.group()
# @click.option('--debug/--no-debug', default=False)
@click.pass_context
def cli(ctx):
    config.load_kube_config()
    ctx.ensure_object(dict)
