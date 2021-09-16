import click
import sys
import getpass
import pyhectiqlab
import pyhectiqlab.ops as ops
from pyhectiqlab.auth import AuthProvider
from pyhectiqlab.artifacts import SharedArtifactsManager
from pyhectiqlab.mlmodels import download_mlmodel as ops_download_mlmodel
from pyhectiqlab.datasets import download_dataset as ops_download_dataset
import socket

@click.group()
def cli():
    """Just a group."""
    pass

@cli.command()
def add_profile():
	auth = AuthProvider()
	username = input("Username: ")

	if auth.profile_exists(username):
		click.echo(f'A profile already exists for {username}')
		return

	password = getpass.getpass(prompt='Password: ', stream=None) 
	click.echo("Connecting...")
	success, api_key_uuid = auth.fetch_secret_api_token(username, password)

	if success:
		click.echo(f'Added profile [{username}] in {auth.tokens_path}')
		try:
			api_name = socket.gethostname()
			res = ops.update_secret_api_token_name(api_key_uuid, name=api_name, token=auth.secret_api_key)
			click.echo(f'Set the API-key name to {api_name}.')
		except:
			return
	else:
		click.echo('Unsuccessful login.')

@cli.command()
def version():
	click.echo(pyhectiqlab.__version__)
	
@cli.command()
def projects():	
	manager = SharedArtifactsManager()
	manager.list_projects()

@cli.command()
@click.option('-p', '--project_id', help='id of the project', required=True)
def artifacts(project_id):
	manager = SharedArtifactsManager()
	manager.select_artifact(project_id)

@cli.command()
@click.option('-p', '--project_id', help='id of the project', required=True)
@click.option('-f', '--filepath', help='Name of the shared artifact', required=True)
def post_artifact(project_id, filepath):
	manager = SharedArtifactsManager()
	click.echo('Pushing artifacts.')
	manager.push_artifact(filepath, project_id)
	click.echo('Artifact pushed')

@cli.command()
@click.option('-p', '--project_id', help='id of the project', required=False)
@click.option('-n', '--name', prompt='MLModel name', help='Name of the mlmodel', required=True)
@click.option('-v', '--version', help='Version of the mlmodel. If not specified, will download the latest release', required=False)
@click.option('-s', '--save_path', prompt='Save path', help='Save path', required=True)
@click.option('-o', '--overwrite', is_flag=True)
def download_mlmodel(project_id, name, version, save_path, overwrite):
	dir_path = ops_download_mlmodel(mlmodel_name=name, 
						project_id=project_id, 
						version=version, 
						save_path=save_path, 
						overwrite=overwrite)
	if dir_path is not None:
		click.echo(f'MLModel saved in {dir_path}')

@cli.command()
@click.option('-p', '--project_id', help='id of the project', required=False)
@click.option('-n', '--name', prompt='Dataset name', help='Name of the dataset', required=True)
@click.option('-v', '--version', help='Version of the dataset. If not specified, will download the latest release', required=False)
@click.option('-s', '--save_path', prompt='Save path', help='Save path', required=True)
@click.option('-o', '--overwrite', is_flag=True)
def download_dataset(project_id, name, version, save_path, overwrite):
	dir_path = ops_download_dataset(dataset_name=name, 
						project_id=project_id, 
						version=version, 
						save_path=save_path, 
						overwrite=overwrite)
	if dir_path is not None:
		click.echo(f'Dataset saved in {dir_path}')
