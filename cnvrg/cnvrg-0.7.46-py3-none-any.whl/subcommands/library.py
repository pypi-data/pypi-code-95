import click
import cnvrg.helpers.cli_helper as cli_helper
from cnvrg.modules.library import Library, DEFAULT_WORKING_DIR
from cnvrg.helpers.logger_helper import log_message
import cnvrg.helpers.export_library_helper as export_library_helper
import os


@click.group()
def library():
    pass

@library.group("library")
def lib_cmd():
    pass

@lib_cmd.command()
@click.argument("library_title")
def info(library_title):
    l = Library(library_title)
    log_message(l)


@lib_cmd.command()
def list():
    [log_message(x) for x in Library.list()]


@lib_cmd.command()
@click.argument("library_title")
@click.option('--working_dir', '-w', default=None, help='working dir')
def clone(library_title, working_dir):
    l = Library(library_title, working_dir=working_dir)
    library_path = l.load(load_model=False)
    log_message("You can find the library in {path}".format(path=library_path), fg='green')



@lib_cmd.command(help="Title")
@click.argument("library_title")
@click.option("--local/--remote", default=False, help="run on your local/remote machine")
@click.option("--arg", multiple=True, help="Add arguments to the cmd in key:value format")
@click.option("--dataset", multiple=True, help="Attach datasets (on remote)")
@click.option("--compute", multiple=True, help="Template to run (on remote)")
@click.option("--working_dir", help="directory to run from", default=None)
@click.option("--title", help="specify experiment title")
def run(library_title, local, arg, dataset, working_dir, compute, title):
    arguments = cli_helper.parse_args(arg)
    datasets = cli_helper.parse_datasets(dataset)
    l = Library(library_title, working_dir=working_dir)
    if local: l.load()
    cli_helper.print_object(l.run(datasets=datasets, computes=compute, title=title, local=local, args=arguments))


@lib_cmd.command(help="Export")
@click.argument("library_files", nargs=-1)
def export(library_files):
    if len(library_files) == 0: library_files = ["."]
    l = Library.export(*library_files)
    log_message(l)


# @lib_cmd()
# @click.option("--working_dir", help="directory to run from", default=None)
# def export(working_dir):
#     export_library_helper.export_library(working_dir=working_dir)