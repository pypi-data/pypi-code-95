import click
import shutil
from iictl.commands import cli
from iictl.crud.pod import get_pod_name_by_label_selector
from iictl.crud.pod import get_pod_log
from iictl.kubectl.kubectl import get_kubectl_logs_command
from iictl.utils.exception import NotFoundError

@cli.command()
@click.option('-f', '--follow', is_flag=True)
@click.option('--tail') # TODO: create with generated name
@click.option('-r', '--raw', is_flag=True)
@click.argument('name')
def logs(follow, tail, raw, name):
    try:
        pod_name = get_pod_name_by_label_selector(
            namespace='notebook',
            label_selector=f'deep.est.ai/app={name}'
        )
    except NotFoundError as e:
        print('Pod not found')
        return
        
    # TODO: listing ii with name and error if ii is not exist or deployment is not ready
    if not raw and shutil.which('kubectl'):
        # TODO: logging change to use logging module
        print('use kubectl logs')
        
        kubectl_command = get_kubectl_logs_command(
            pod_name=pod_name,
            namespace='notebook',
            follow=follow,
            tail=tail,
        )
        
        import subprocess
        subprocess.call(kubectl_command)
    else:
        print('use python logs')
        resp = get_pod_log(
            name=pod_name,
            namespace='notebook',
            follow=follow,
            tail=tail,
        )
    
        for line in resp:
            print(line.decode('utf-8'), end='')
