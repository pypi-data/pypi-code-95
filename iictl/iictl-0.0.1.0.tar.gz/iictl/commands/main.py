import click
from kubernetes import client, config
from iictl.utils.click import global_option

@click.group()
@click.pass_context
@click.option('-n', '--namespace', type=str, help='name of namespace', callback=global_option)
def cli(ctx, namespace):
    config.load_kube_config()
    ctx.ensure_object(dict)
    
    
