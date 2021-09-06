import click
import iictl.utils.parse as parse
from iictl.commands.main import cli
from iictl.crud.integrated_instance import create_integrated_instance
from iictl.format.integrated_instance import get_integrated_instance_format
from iictl.utils.exception import ParseError, PortError, AlreadyExistError

@cli.command()
@click.option('--name') # TODO: create with generated name
@click.option('-e', '--env', multiple=True) # name=value
@click.option('-v', '--volume', multiple=True) # pvcname:mountpath:ro
@click.option('--domain', multiple=True) # port:domain
@click.option('-w', '--workdir', 'working_dir')
@click.argument('image')
@click.argument('command', nargs=-1)
def run(name, env, volume, domain, working_dir, image, command):
    try:
        envs = parse.parse_envs(env)
        volumes = parse.parse_volumes(volume)
        lb = parse.parse_domains(domain)
    except ParseError as e:
        print(str(e))
        exit(1)
    except PortError as e:
        print(str(e))
        exit(1)
        
    
    ii = get_integrated_instance_format(
        name=name,
        namespace='notebook',
        image=image,
        command=command,
        lb=lb,
        envs=envs,
        volume_mounts=volumes,
        working_dir=working_dir,
    #     resources: Di
#         node_selector: Dict[str, str]
    )
    
    try:
        create_integrated_instance(
            namespace='notebook',
            integrated_instance=ii
        )
    except AlreadyExistError as e:
        print(f'integrated instance {name} is already exist')
        exit(1)
    
    print('resource create requested')