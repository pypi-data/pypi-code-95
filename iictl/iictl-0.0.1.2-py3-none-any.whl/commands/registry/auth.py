import click
import base64, json
import os.path
from iictl.commands.registry.main import registry
from iictl.format.secret import get_secret_format
from iictl.crud.secret import create_secret
from iictl.utils.exception import AlreadyExistError
from iictl.utils.click import global_option
from iictl.utils.parse import verify_object_name

@registry.command(help='auth specific registry')
@click.option('--from-cli', is_flag=True)
@click.option('--from-file', type=str, help='auth file (usually ~/.docker.config.json)')
@click.option('-n', '--namespace', type=str, help='name of namespace', callback=global_option)
@click.argument('name', type=str)
def auth(from_cli, from_file, name, namespace):
    if not verify_object_name(name):
        click.echo('wrong object name')
        return 
    
    if (from_cli == True and from_file is not None) or (from_cli == False and from_file is None):
        click.echo('you must select exactly one "from_" option.')
        return

    if from_cli:
        server = click.prompt('Container image registry address', type=str, default='docker.io')
        username = click.prompt('Username', type=str)
        password = click.prompt('Password', type=str, hide_input=True)
        
        cred_payload = {
            "auths": {
                server: {
                    "Username": username,
                    "Password": password,
                }
            }
        }

        cred_payload = json.dumps(cred_payload)
    elif from_file:
        if not os.path.exists(from_file) or not os.path.isfile(from_file):
            click.echo('enter a valid file path.')
            return
            
        with open(from_file, 'r') as f:
            cred_payload = f.read()
            
    data = {
        ".dockerconfigjson": base64.b64encode(
            cred_payload.encode()
        ).decode()
    }
        
    secret = get_secret_format(
        name=name,
        data=data,
        type_="kubernetes.io/dockerconfigjson",
    )
    
    try:
        create_secret(
            name=name,
            namespace=namespace,
            secret=secret,
        )
        click.echo(f'A secret "{name}" creation was requested.')
    except AlreadyExistError as e:
        click.echo(f'A secret "{name}" already exist')
