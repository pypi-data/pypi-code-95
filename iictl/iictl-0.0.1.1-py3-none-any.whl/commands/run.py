import click
import iictl.utils.parse as parse
from iictl.commands.main import cli
from iictl.crud.integrated_instance import create_integrated_instance
from iictl.format.integrated_instance import get_integrated_instance_format
from iictl.utils.exception import ParseError, PortError, AlreadyExistError
from iictl.utils.click import global_option
from iictl.utils.parse import verify_object_name

@cli.command(help='run instance')
@click.option('--name', type=str, help='instance name') # TODO: create with generated name
@click.option('--gpus', default=0, type=int, help='gpu resource request')
@click.option('--cpus', default='20', type=str, help='cpu resource limits')
@click.option('-e', '--env', type=str, multiple=True, help='environment variables') # name=value
@click.option('-v', '--volume', type=str, multiple=True, help='volume mapping') # pvcname:mountpath:ro
@click.option('--domain', type=str, multiple=True, help='port to domain mapping') # port:domain
@click.option('-w', '--workdir', 'working_dir', type=str, help='working directory')
@click.option('--image-pull-secret', type=str, help='docker registry auth name')
@click.option('-n', '--namespace', type=str, help='name of namespace', callback=global_option)
@click.argument('image')
@click.argument('command', nargs=-1)
def run(name, namespace, env, volume, domain, working_dir, image_pull_secret, image, command, gpus: int, cpus: str):
    if not verify_object_name(name):
        click.echo('wrong object name')
        return 
    
    try:
        envs = parse.parse_envs(env)
        volumes = parse.parse_volumes(volume)
        lb = parse.parse_domains(domain)
    except ParseError as e:
        click.echo(str(e))
        exit(1)
    except PortError as e:
        click.echo(str(e))
        exit(1)
        
    if gpus == 0:
        envs.append(('NVIDIA_VISIBLE_DEVICES', 'none'))
        
    ii = get_integrated_instance_format(
        name=name,
        image=image,
        command=command,
        lb=lb,
        envs=envs,
        volume_mounts=volumes,
        working_dir=working_dir,
        gpus=gpus,
        cpus=cpus,
        image_pull_secret=image_pull_secret,
#         node_selector: Dict[str, str]
    )
    
    try:
        create_integrated_instance(
            namespace=namespace,
            integrated_instance=ii
        )
    except AlreadyExistError as e:
        click.echo(f'integrated instance {name} is already exist')
        exit(1)
    
    click.echo('resource create requested')