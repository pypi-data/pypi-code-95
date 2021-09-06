import click
import shutil
from iictl.commands import cli
from iictl.crud.stream import get_exec_stream_pod
from iictl.crud.pod import get_pod_name_by_label_selector
from iictl.kubectl.kubectl import get_kubectl_exec_command
from iictl.utils.shell_executor import ShellExecutor
from iictl.utils.exception import NotFoundError

@cli.command()
@click.option('-i', '--stdin', is_flag=True)
@click.option('-t', '--tty', is_flag=True)
@click.argument('name')
@click.argument('command', nargs=-1)
def exec(name, command, stdin, tty):
    try:
        pod_name = get_pod_name_by_label_selector(
            namespace='notebook',
            label_selector=f'deep.est.ai/app={name}'
        )
    except NotFoundError as e:
        print('Pod not found')
        return
    
    # TODO: listing ii with name and error if ii is not exist or deployment is not ready
    if shutil.which('kubectl'):
        # TODO: logging change to use logging module
        print('use kubectl exec')
        
        kubectl_command = get_kubectl_exec_command(
            pod_name=pod_name,
            namespace='notebook',
            command=command,
            stdin=stdin,
            tty=tty
        )
        
        import subprocess
        subprocess.call(kubectl_command)
    else:
        print('use python shell')
        stream = get_exec_stream_pod(
            name=pod_name,
            namespace='notebook',
            command=command,
            stdin=stdin,
            tty=tty
        )

        executor = ShellExecutor(k8s_stream=stream)
        executor.spawn()