#!/usr/bin/env python
import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


import os.path

def readver(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()

def get_version(rel_path):
    for line in readver(rel_path).splitlines():
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")

setup(
    name="read_vme_offline",
    description="Automatically created environment for python package",
    url="http://gitlab.com/npicas/read_vme_offline",
    author="anastasia_jaromrax",
    author_email="ojr@ujf.cas.cz",
    license="GPL2",
    version=get_version("read_vme_offline/version.py"),
    packages=["read_vme_offline"],
    package_data={'read_vme_offline': ['data/*']},
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    scripts = ['bin/read_vme_offline'],
    install_requires = ['fire','pympler','pylatex','h5py','root_numpy','tabulate','tables']

)
#    install_requires = ['numpy==1.16.2'],
#
#   To RECOVER AND ACCESS THE Data later in module: :
#  X DATA_PATH = pkg_resources.resource_filename('read_vme_offline', 'data/')
#  X DB_FILE =   pkg_resources.resource_filename('read_vme_offline', 'data/file')
#   DB_FILE = pkg_resources.resource_filename(
#       pkg_resources.Requirement.parse('nuphy2'),
#       'data/nubase2016.txt'
#   )
#   pip install -e .
#   bumpversion patch minor major release
#      release needed for pypi
