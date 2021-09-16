#!/usr/bin/env python3
'''Belette - Generates licensing information for dependencies for Conan projects

Usage:
  belette generate <path> <output_file>
  belette (-h | --help)
  belette --version

Commands:
  generate  Creates a file that contains information about all the dependencies
            of a project and their associated licenses. <path> must point to the
            root of a Conan project, which should contain conanfile.py or
            conanfile.txt. <output_file> must be a .hpp file.

Options:
  -h --help    Show this screen.
  --version    Show version.

'''

import os

from conans.client.conan_api import ConanAPIV1
from textwrap import dedent
from docopt import docopt
import jinja2


def main():
    arguments = docopt(__doc__, version='Belette')
    if arguments['generate']:
        generate(arguments['<path>'], arguments['<output_file>'])


def generate(path, output_file):
    if not output_file.endswith('.hpp'):
        raise ValueError("Output file should end in .hpp")

    cwd = os.path.dirname(os.path.realpath(__file__))
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(
        os.path.join(cwd, 'templates')),
                             undefined=jinja2.StrictUndefined,
                             trim_blocks=True)
    template = env.get_template('template.hpp')

    info = {
        'generated_file_warning':
        dedent('''\
            WARNING: this file is generated, do not edit manually, nor commit
            to source control. Your changes will be overriden'''),
        'packages': [],
        'licenses': {}
    }

    api = ConanAPIV1()
    graph, _ = api.info(path)
    for node in graph.nodes:
        if node is graph.root:
            continue # this node is not a dependency
        if node.conanfile.license == "proprietary":
            continue # this node is not open-source
        info['packages'].append({
            'name': node.name,
            'license': node.conanfile.license,
            'version': node.conanfile.version,
            'homepage': node.conanfile.homepage
        })

    for package in info['packages']:
        lic = package['license']
        if lic not in info['licenses']:
            licpath = "{}/licenses/{}.txt".format(cwd, lic)
            if not os.path.isfile(licpath):
                raise ValueError("Could not find full license text for license {}". format(lic))
            with open(licpath, 'r') as licfile:
                info['licenses'][lic] = licfile.read()

    with open(output_file, 'w') as ofile:
        ofile.write(template.render(info))


if __name__ == "__main__":
    main()
