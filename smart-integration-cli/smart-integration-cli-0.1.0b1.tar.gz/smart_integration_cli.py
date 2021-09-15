import os
import click
from time import sleep
from color_print import print

from smart_cli.generators.structure import Structure
from smart_cli.generators.docker_structure import (
    DjangoDockerAPPStructure,
    FastAPIDockerAPPStructure,
)


@click.group()
def cli():
    pass


@cli.command()
@click.option('--name', default='project', help='This name of your project')
@click.argument('name', type=click.STRING, default='project', required=True)
@click.option(
    '--auth_type', default='basic', help='Choose type of your project(oauth, basic)'
)
@click.argument('auth_type', type=click.STRING, default='basic', required=True)
def zappa_django_init(name, auth_type):
    if auth_type.lower() not in ('basic', 'oauth'):
        print(
            f"{auth_type} invalid integration type, must be on of {['basic', 'oauth']}",
            color='yellow',
            tag='error',
            tag_color='red',
        )
        return None
    if name in os.listdir('.'):
        print(
            f'Project with name - {name} exists in this folder.',
            color='yellow',
            tag='error',
            tag_color='red',
        )
        return None

    struct = Structure(name, auth_type)
    print('~~~ install dependencies ~~~', color='blue', tag='start', tag_color='blue')
    struct.install_dependencies()
    print(
        '~~~ Finish install dependencies ~~~',
        color='green',
        tag='complete',
        tag_color='green',
    )
    print('~~~ django app ~~~', color='blue', tag='start', tag_color='blue')
    sleep(1)
    struct.init_django_app()
    print('~~~ Finish ~~~', color='green', tag='complete', tag_color='green')
    print('~~~ manage applications ~~~', color='blue', tag='start', tag_color='blue')
    sleep(0.5)
    struct.rewrite_basic_files()
    sleep(1.5)
    struct.generate_api_apps_files()
    sleep(1.5)
    print('~~~ Finish ~~~', color='green', tag='complete', tag_color='green')
    print('~~~ template done. ~~~ ', color='green', tag='success', tag_color='green')


@cli.command()
@click.option(
    '--name', type=click.STRING, help='This name of your project', required=True
)
@click.option(
    '--auth_type',
    type=click.STRING,
    default='basic',
    help='Choose type of your project(oauth, basic)',
    required=True,
)
@click.option('--registry', help='regeistry path like "localhost:5000/"')
@click.option('--network', type=click.STRING, required=True, help='external network')
def django_init(name, registry, auth_type, network):
    if auth_type.lower() not in ('basic', 'oauth'):
        print(
            f"{auth_type} invalid integration type, must be on of {['basic', 'oauth']}",
            color='yellow',
            tag='error',
            tag_color='red',
        )
        return None
    if name in os.listdir('.'):
        print(
            f'Project with name - {name} exists in this folder.',
            color='yellow',
            tag='error',
            tag_color='red',
        )
        return None
    os.mkdir(name)
    os.chdir(name)
    struct = DjangoDockerAPPStructure(name, auth_type, registry, network)
    print('~~~ install dependencies ~~~', color='blue', tag='start', tag_color='blue')
    struct.install_dependencies()
    print(
        '~~~ Finish install dependencies ~~~',
        color='green',
        tag='complete',
        tag_color='green',
    )
    print('~~~ manage docker files ~~~', color='blue', tag='start', tag_color='blue')
    sleep(3)
    struct.generate_docker_folder()
    struct.generate_docker_compose_file()
    struct.generate_gitlab_ci_file()
    print('~~~ Finish ~~~', color='green', tag='complete', tag_color='green')
    print('~~~ django app ~~~', color='blue', tag='start', tag_color='blue')
    sleep(2)
    struct.init_django_app()
    print('~~~ Finish ~~~', color='green', tag='complete', tag_color='green')
    print('~~~ manage settings files ~~~', color='blue', tag='start', tag_color='blue')
    sleep(1.5)
    struct.rewrite_basic_files()
    print('~~~ Finish ~~~', color='green', tag='complete', tag_color='green')
    print(
        '~~~ manage application files ~~~', color='blue', tag='start', tag_color='blue'
    )
    sleep(1.5)
    struct.generate_api_apps_files()
    sleep(1.5)
    struct.generate_requirements_files()
    print('~~~ Finish ~~~', color='green', tag='complete', tag_color='green')
    print('~~~ template done. ~~~ ', color='green', tag='success', tag_color='green')


@cli.command()
@click.option(
    '--name', type=click.STRING, help='This name of your project', required=True
)
@click.option(
    '--auth_type',
    type=click.STRING,
    default='basic',
    help='Choose type of your project(oauth, basic)',
    required=True,
)
@click.option('--registry', help='regeistry path like "localhost:5000/"')
@click.option(
    '--network', type=click.STRING, default='nginx_network', help='external network'
)
def fastapi_init(name, registry, auth_type, network):
    if auth_type.lower() not in ('basic', 'oauth'):
        print(
            f"{auth_type} invalid integration type, must be on of {['basic', 'oauth']}",
            color='yellow',
            tag='error',
            tag_color='red',
        )
        return None
    if name in os.listdir('.'):
        print(
            f'Project with name - {name} exists in this folder.',
            color='yellow',
            tag='error',
            tag_color='red',
        )
        return None
    os.mkdir(name)
    os.chdir(name)
    struct = FastAPIDockerAPPStructure(name, auth_type, registry, network)
    print('~~~ manage docker files ~~~', color='blue', tag='start', tag_color='blue')
    sleep(3)
    struct.generate_docker_folder()
    struct.generate_docker_compose_file()
    struct.generate_gitlab_ci_file()
    print(
        '~~~ Finish manage docker files ~~~',
        color='green',
        tag='complete',
        tag_color='green',
    )
    print('~~~ install dependencies ~~~', color='blue', tag='start', tag_color='blue')
    struct.install_dependencies()
    print(
        '~~~ Finish install dependencies ~~~',
        color='green',
        tag='complete',
        tag_color='green',
    )

    print(
        '~~~ create project structure ~~~', color='blue', tag='start', tag_color='blue'
    )
    struct.init_app()
    struct.generate_requirements_files()
    struct.write_main_files()
    struct.generate_core_files()
    struct.generate_config_files()
    sleep(3)
    print('~~~ Finish ~~~', color='green', tag='complete', tag_color='green')
    sleep(1.2)
    print('~~~ template done. ~~~ ', color='green', tag='success', tag_color='green')
