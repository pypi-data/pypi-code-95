from setuptools import setup, find_packages

from os import path
from io import open
# import yaml

here = path.abspath(path.dirname(__file__))
reqs = []

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# with open(path.join(here, 'release.yaml'), encoding='utf-8') as f:
#     release = yaml.safe_load(f.read())

#version = release['release'][0]['version']
# repo = release['release'][0]['repo']

# with open(path.join(here, 'requirements.txt'), encoding='utf-8') as f:
#     read_lines = f.readlines()
#     reqs = [each.strip() for each in read_lines]

from distutils import dir_util
from distutils.command import build
import os#, sys, re

class Build(build.build):
    """
    * Clear build path before building
    """
    def run(self):
        print("Removing prior-built items...", end=" ")

        build_dir = 'build/lib/widen'
        if os.path.exists(build_dir):
            dir_util.remove_tree(build_dir)

        for root, dirs, files in os.walk('.'):
            for item in files:
                if item.endswith('.pyc'):
                    os.remove(os.path.join(root, item))

        print("Done")
        # global path

        # ## Make sure build directory is clean
        # buildPath = os.path.join(path, self.build_lib)
        # if os.path.isdir(buildPath):
        #     distutils.dir_util.remove_tree(buildPath)
    
        # ret = build.build.run(self)

from distutils.command.clean import clean as CleanCommand
from distutils.dir_util import remove_tree

class Clean(CleanCommand):
    print("Cleanning...", end=" ")
    user_options = CleanCommand.user_options + [
        ('build-coverage=', 'c',
         "build directory for coverage output (default: 'build/coverage')"),
        ('build-tox=', 't',
         "build directory for tox (default: '.tox')"),
    ]

    def initialize_options(self):
        self.build_coverage = None
        self.build_help = None
        self.build_tox = None
        CleanCommand.initialize_options(self)

    def run(self):
        if self.all:
            for directory in (os.path.join(self.build_base, 'coverage'),
                              os.path.join('dist'),
                              os.path.join('.tox'),
                              os.path.join(self.build_base, 'help')):
                if os.path.exists(directory):
                    remove_tree(directory, dry_run=self.dry_run)
                else:
                    log.warn("'%s' does not exist -- can't clean it",
                             directory)
        if self.build_coverage:
            remove_tree(self.build_coverage, dry_run=self.dry_run)
        if self.build_help:
            remove_tree(self.build_help, dry_run=self.dry_run)
        if self.build_tox:
            remove_tree(self.build_tox, dry_run=self.dry_run)
        CleanCommand.run(self)

from setuptools.command.test import test as TestCommand
import sys
class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = ['tests']

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest

        errno = pytest.main(self.pytest_args)
        sys.exit(errno)

from distutils.core import setup
from distutils.command.clean import clean
from distutils.command.install import install

class MyInstall(install):

    # Calls the default run command, then deletes the build area
    # (equivalent to "setup clean --all").
    def run(self):
        install.run(self)
        c = clean(self.distribution)
        c.all = True
        c.finalize_options()
        c.run()


setup(
    name='widen',
    version = '0.0.1.dev0',
    cmdclass={'build': Build,
              'test': PyTest,
              'clean': Clean,
              'clean2': MyInstall},

    author = "Lucas Nunes",
    url = 'https://github.com/lnunesai/Widen.git',
    author_email = 'lnunesai@gmail.com',
    description = "Package project for learning purposes.",

    long_description=long_description, #open('README.md').read(),
    long_description_content_type="text/markdown",
    
    license='MIT',

    classifiers = [
        'Development Status :: 1 - Planning',
        'Intended Audience :: Education',
        #'Topic :: Software Development :: Build Tools',
        "License :: OSI Approved :: MIT License",
        #'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        #'Programming Language :: Python :: 2.7',
        "Programming Language :: Python :: 3",
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],

    keywords = 'widen learn',

    python_requires='>=3.6',

    package_dir={"": "src/python"},
    packages=find_packages("src/python"),

    install_requires=['typer'],
    extras_require={'infer': ['numpy'], 'testing': ['pytest']},
    entry_points={
        'console_scripts': [
            'widen = widen.cli.cli:app',
            'widen2 = widen.cli.cli:app',
        ]
    },
    # entry_points={
    #     'console_scripts': [
    #         'animals=basics.animals.__main__:main',
    #     ],
    #     'animals': [
    #         'cat=basics.animals.models:Cat',
    #         'dog=basics.animals.models:Dog',
    #         'cow=basics.animals.models:Cow',
    #     ],
    # },
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    package_data={"": ["data/*.tx2", "data/*.txt"], 'widen': ['data/addresses.csv']},
)