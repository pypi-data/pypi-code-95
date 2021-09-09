from cnvrg.subcommands.library import library as lib_cli
from cnvrg.subcommands.project import project as project_cli
from cnvrg.subcommands.cnvrg import cnvrg as cnvrg_cli
import click




cli = click.CommandCollection(sources=[lib_cli, project_cli, cnvrg_cli])



if __name__ == '__main__':
    cli()
















