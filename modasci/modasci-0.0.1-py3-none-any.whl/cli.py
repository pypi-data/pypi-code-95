import argparse
import pathlib

import munch
import yaml

from .workflow import Workflow


def run():
    """
    Parses the command-line arguments, sets up a workflow based on the passed `config`, and initiates the execution.
    The function is bound to the package's main entry point, as well as its console entry point.
    """
    # ToDo: Bound the function as the package's console entry point.
    parser = argparse.ArgumentParser(prog='rodasci', description='Executes the described workflow.')
    parser.add_argument('config', type=pathlib.Path, nargs='?', default='workflow.yaml', help='YAML blueprint.')
    arguments = parser.parse_args()
    with open(arguments.config, 'r') as stream:
        plainWorkflow = yaml.full_load(stream)
        plainWorkflow = munch.munchify(plainWorkflow)
    workflow = Workflow(plainWorkflow)
    workflow.start()
