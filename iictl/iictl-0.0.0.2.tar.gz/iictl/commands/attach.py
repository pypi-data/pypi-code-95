import click
import shutil
from iictl.commands import cli
from iictl.crud.stream import get_attach_stream_pod
from iictl.crud.pod import get_pod_name_by_label_selector
from iictl.utils.shell_executor import ShellExecutor
from iictl.kubectl.kubectl import get_kubectl_attach_command
from iictl.utils.exception import NotFoundError

@cli.command()
@click.option('-i', '--stdin', is_flag=True)
@click.option('-t', '--tty', is_flag=True)
@click.option('-r', '--raw', is_flag=True)
@click.argument('name')
def attach(name, stdin, tty, raw):
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
        print('use kubectl attach')
        
        kubectl_command = get_kubectl_attach_command(
            pod_name=pod_name,
            namespace='notebook',
            stdin=stdin,
            tty=tty
        )
        
        import subprocess
        subprocess.call(kubectl_command)
    else:
#         raise NotImplemented
        print('use python shell')
        print("If you don't see a command prompt, try pressing enter.")
        stream = get_attach_stream_pod(
            name=pod_name,
            namespace='notebook',
            stdin=stdin,
            tty=tty
        )

        executor = ShellExecutor(k8s_stream=stream, stdin=stdin)
        executor.spawn()