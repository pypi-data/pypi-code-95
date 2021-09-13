import click
import shutil
from iictl.commands import cli
from iictl.crud.stream import get_attach_stream_pod
from iictl.crud.pod import get_pod_name_by_label_selector
from iictl.utils.shell_executor import ShellExecutor
from iictl.kubectl.kubectl import get_kubectl_attach_command, get_executable
from iictl.utils.exception import NotFoundError
from iictl.utils.click import global_option

@cli.command(help='attach to instance')
@click.option('-i', '--stdin', is_flag=True)
@click.option('-t', '--tty', is_flag=True)
@click.option('-r', '--raw', is_flag=True)
@click.option('-n', '--namespace', type=str, help='name of namespace', callback=global_option)
@click.argument('name')
def attach(name, namespace, stdin, tty, raw):
    try:
        pod_name = get_pod_name_by_label_selector(
            namespace=namespace,
            label_selector=f'deep.est.ai/app={name}'
        )
    except NotFoundError as e:
        click.echo('Pod not found')
        return
    
    
    executable = get_executable()
    # TODO: listing ii with name and error if ii is not exist or deployment is not ready
    if executable:
        # TODO: logging change to use logging module
        kubectl_command = get_kubectl_attach_command(
            pod_name=pod_name,
            namespace=namespace,
            stdin=stdin,
            tty=tty,
            executable=executable,
        )
        
        import subprocess
        subprocess.call(kubectl_command)
    else:
#         raise NotImplemented
        click.echo('use python shell')
        click.echo("If you don't see a command prompt, try pressing enter.")
        stream = get_attach_stream_pod(
            name=pod_name,
            namespace=namespace,
            stdin=stdin,
            tty=tty
        )

        executor = ShellExecutor(k8s_stream=stream, stdin=stdin)
        executor.spawn()