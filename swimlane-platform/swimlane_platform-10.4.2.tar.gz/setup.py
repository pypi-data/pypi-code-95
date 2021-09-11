from setuptools import setup, Command
from distutils.command.register import register as register_orig
from distutils.command.upload import upload as upload_orig
import shutil
import os
import sys
from glob import glob
from json import load


def convert(value):
    """Converts some specific json objects to python object"""
    if isinstance(value, dict):
        return {convert(k): convert(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [convert(element) for element in value]
    elif sys.version_info[0] == 2 and isinstance(value, unicode):
        return value.encode("utf-8")
    else:
        return value


def readme():
    with open('README.md') as f:
        return f.read()


def requirements():
    with open('requirements.txt') as f:
        return f.read().splitlines()


def super_glob(*path):
    files = []
    for arg in path:
        files.extend(glob(arg))
    return files


class Register(register_orig):

    def _get_rc_file(self):
        return os.path.join('.', '.pypirc')


class Upload(upload_orig):

    def _get_rc_file(self):
        return os.path.join('.', '.pypirc')


class Clean(Command):
    """Custom clean command to tidy up the project root."""
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    # noinspection PyMethodMayBeStatic
    def run(self):
        shutil.rmtree('build', ignore_errors=True)
        shutil.rmtree('swimlane_platform.egg-info', ignore_errors=True)


with open('setup.json', 'r') as config_file:
    config = load(config_file, object_hook=convert)

setup(
    packages=['swimlane_platform',
              'swimlane_platform.lib',
              'swimlane_platform.install_steps',
              'swimlane_platform.shared_steps',
              'swimlane_platform.upgrade_steps',
              'swimlane_platform.backup'],
    long_description=readme(),
    long_description_content_type="text/markdown",
    install_requires=requirements(),
    include_package_data=True,
    cmdclass={
        'clean': Clean,
        'register': Register,
        'upload': Upload
    },
    entry_points={
        'console_scripts': ['swimlane-platform=swimlane_platform.wizard:run'],
    },
    data_files=[
        ('', ['setup.json']),
        ('swimlane_template_dir', glob('swimlane_template_dir/*.yml')),
        ('swimlane_template_dir/db-init', glob('swimlane_template_dir/db-init/*.sh')),
        ('swimlane_template_dir/.secrets', glob('swimlane_template_dir/.secrets/.*'))
    ],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.6"
    ],
    **config
)
