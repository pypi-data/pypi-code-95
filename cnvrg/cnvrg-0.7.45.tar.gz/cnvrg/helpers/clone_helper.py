import click
from cnvrg.modules.project import Project

def clone_project(project_url):
    owner_slug, project_slug = Project.get_owner_and_project_from_url(project_url)
    click.secho("Cloning {}".format(project_slug), fg="green")
    project = Project(owner_slug=owner_slug, project_slug=project_slug)
    click.secho(project.clone())



def test_experiment(project_url, command):
    owner_slug, project_slug = Project.get_owner_and_project_from_url(project_url)
    project = Project(owner_slug=owner_slug, project_slug=project_slug)
    exp = project.create_experiment(command, title="Hello Test ME :D")

