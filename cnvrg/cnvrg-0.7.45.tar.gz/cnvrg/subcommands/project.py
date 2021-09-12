import click
import os
import cnvrg.actions.project_actions  as project_actions



@click.group()
@click.option("--log-level", default="INFO", help="log level")
def project(log_level):
    pass

@project.command()
@click.option('--working_dir', '-w', default=os.getcwd(), help='working dir')
@click.option('--commit', '-c', default=None, help='commit to clone')
@click.argument("project_path")
def clone(project_path, working_dir, commit):
    project_actions.clone(project_path, working_dir=working_dir, commit_sha1=commit)

@project.command()
def download():
    project_actions.download()


@project.command()
def upload():
    project_actions.upload()
