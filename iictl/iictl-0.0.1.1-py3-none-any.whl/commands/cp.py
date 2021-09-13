import click
import shutil
from iictl.commands import cli
from iictl.crud.pod import get_pod_name_by_label_selector
from iictl.kubectl.kubectl import get_kubectl_cp_command, get_executable
from iictl.utils.exception import NotFoundError
from iictl.utils.click import global_option
from iictl.utils.parse import verify_object_name

@cli.command(help='copy local file to instance / remote file to local')
@click.option('-n', '--namespace', type=str, help='name of namespace', callback=global_option)
@click.argument('from_path')
@click.argument('to_path')
def cp(from_path, to_path, namespace):
    if ':' in from_path and ':' in to_path:
        click.echo('cannot execute remote file to remote file copy')
        return
    
    if ':' not in from_path and ':' not in to_path:
        click.echo('cannnot execute local to local file copy')
        return
    
    if ':' in from_path:
        ii_name, path = from_path.split(':')
    else:
        ii_name, path = to_path.split(':')
    
    if not verify_object_name(ii_name):
        click.echo('wrong object name')
        return 
    
    try:
        pod_name = get_pod_name_by_label_selector(
            namespace=namespace,
            label_selector=f'deep.est.ai/app={ii_name}'
        )
    except NotFoundError as e:
        click.echo('Pod not found')
        return
    
    if ':' in from_path:
        from_path = f'{pod_name}:{path}'
    else:
        to_path = f'{pod_name}:{path}'    
    
    executable = get_executable()
    # TODO: listing ii with name and error if ii is not exist or deployment is not ready
    if executable:
        # TODO: logging change to use logging module
        kubectl_command = get_kubectl_cp_command(
            namespace=namespace,
            from_path=from_path,
            to_path=to_path,
            executable=executable,
        )
        
        import subprocess
        subprocess.call(kubectl_command)
    else:
        raise NotImplementedError