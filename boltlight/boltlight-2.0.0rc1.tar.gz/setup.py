# Boltlight - a LN node wrapper
#
# Copyright (C) 2021 boltlight contributors
# Copyright (C) 2018 inbitcoin s.r.l.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# For a full list of contributors, please see the AUTHORS.md file.
"""Module to bundle boltlight with setuptools."""

import sys

from contextlib import redirect_stdout, suppress
from distutils.cmd import Command
from distutils.command.build_py import build_py
from distutils.command.clean import clean
from fileinput import input as finput
from importlib import import_module
from io import StringIO
from os import chdir, chmod, linesep, makedirs, path, remove, stat, walk
from pathlib import Path
from shutil import move, rmtree, which
from stat import S_IXGRP, S_IXOTH, S_IXUSR
from subprocess import Popen, TimeoutExpired
from urllib.request import urlretrieve
from zipfile import ZipFile

from pip._vendor.distlib.scripts import ScriptMaker
from pkg_resources import resource_filename
from setuptools import setup
from setuptools.command.develop import develop
from setuptools.command.sdist import sdist
from setuptools.command.test import test as TestCommand

# directories
B_DIR = 'boltlight'
E_DIR = 'examples'
R_DIR = 'reports'
U_DIR = path.sep.join([B_DIR, 'utils'])
MIGRATIONS_DIR = path.sep.join([B_DIR, 'migrations'])
MGR_VERSIONS_DIR = path.sep.join([MIGRATIONS_DIR, 'versions'])

# boltlight
PROTO = 'boltlight.proto'

# blink
CLI_NAME = 'blink'
CLI_ENTRY = f'{CLI_NAME} = {B_DIR}.{CLI_NAME}:entrypoint'
SHELLS = ['bash', 'zsh']
COMPLETION_SCRIPTS = {}
for SHELL in SHELLS:
    COMPLETION_SCRIPTS[SHELL] = f'complete-{CLI_NAME}-{SHELL}.sh'

# c-lightning
CL_VER = '0.10.1'

# lnd
LND_REF = 'v0.13.1-beta'
LND_PROTOS = ['rpc.proto', 'walletunlocker.proto']
GOOGLE = 'google'
GAPIS = 'googleapis'
GAPIS_MASTER = GAPIS + '-master'
GAPIS_ZIP = GAPIS + '.zip'

# linting
PYCODESTYLE_EXCLUDE = ['*_pb2*.py', 'env.py']
PYLINT_ARGS = ['--persistent=y', B_DIR]

# cleanup
CLEANUP_SUFFIXES = ['_pb2.py', '_pb2_grpc.py', '.pyc', '.so', '.o']

# data files
EXAMPLES = [path.as_posix() for path in Path(E_DIR).glob('*')] + \
    [path.sep.join([E_DIR, COMPLETION_SCRIPTS[shell]]) for shell in SHELLS]
DOC = [path.as_posix() for path in Path('.').glob('*.md')] + \
    [path.as_posix() for path in Path('doc').glob('*.md')] + \
    ['COPYING']

# dependencies
RUNTIME_DEPS = [
    'alembic~=1.5.5',
    'click~=7.1.2',
    'googleapis-common-protos~=1.53.0',
    'grpcio~=1.38.0',
    'macaroonbakery~=1.3.1',
    'protobuf~=3.15.3',
    'pylibscrypt~=1.8.0',
    'pyln-client==' + CL_VER,
    'pymacaroons~=0.13.0',
    'pynacl~=1.3.0',
    'qrcode~=6.1',
    'requests~=2.25.1',
    'SQLAlchemy~=1.3.23',
]
SETUP_DEPS = [
    'click~=7.1.2',
    'docutils~=0.16',
    'grpcio-tools~=1.38.0',
    'grpcio~=1.38.0',
    'protobuf~=3.15.8',
    'pycodestyle==2.7.0',
    'pylint==2.10.2',
    'pylint-protobuf==0.20.2',
]


def _die(message):
    """Prints message to stderr with error code 1."""
    sys.stderr.write(message)
    sys.exit(1)


def _try_rm(tree):
    """Try to remove a directory or file, without failing if missing."""
    with suppress(OSError):
        rmtree(tree)
    with suppress(OSError):
        remove(tree)


def _download_lnd_deps():
    """Download lnd's proto file for the supported version and googleapis."""
    chdir(B_DIR)
    lnd_url = 'https://raw.githubusercontent.com/lightningnetwork/lnd'
    for lnd_proto in LND_PROTOS:
        urlretrieve(f'{lnd_url}/{LND_REF}/lnrpc/{lnd_proto}', lnd_proto)
    googleapis_url = f'https://github.com/{GAPIS}/{GAPIS}/archive/master.zip'
    urlretrieve(googleapis_url, GAPIS_ZIP)
    with ZipFile(GAPIS_ZIP, 'r') as zip_ref:
        start_member = GAPIS_MASTER + '/google/'
        files = [
            n for n in zip_ref.namelist()
            if n.startswith(start_member) and not n.endswith('/')
        ]
        zip_ref.extractall('.', members=files)
    _try_rm(GAPIS_ZIP)
    if path.exists(GOOGLE):
        rmtree(GOOGLE)
    move(path.sep.join([GAPIS_MASTER, GOOGLE]), GOOGLE)
    _try_rm(GAPIS_MASTER)
    chdir('..')


def _gen_shell_completion(shell, cli_in_path):
    """Generate CLI completion files for the supported shells."""
    final_dest = path.join(E_DIR, COMPLETION_SCRIPTS[shell])
    if not which(shell):
        Path(final_dest).touch()
        print(f'Shell {shell} is not installed, creating empty completion '
              'script')
        return
    source = f'source_{shell}'
    cli_path = CLI_NAME if cli_in_path else path.abspath(CLI_NAME)
    cmd = [
        shell, '-c', '_{}_COMPLETE={} {} > {}'.format(CLI_NAME.upper(), source,
                                                      cli_path, final_dest)
    ]
    proc = Popen(cmd)
    try:
        _, _ = proc.communicate(timeout=10)
        print('Created completion script for', shell)
    except TimeoutExpired:
        proc.kill()
    status = stat(final_dest)
    chmod(final_dest, status.st_mode | S_IXUSR | S_IXGRP | S_IXOTH)


def _gen_proto(opts):
    """Generate python code from given proto file."""
    print('Generating proto files from', opts[-1])
    if not path.exists(opts[-1]):
        _die("Can't find required file: " + opts[-1])
    try:
        # pylint: disable=import-outside-toplevel
        from grpc_tools.protoc import main as run_protoc
        # pylint: enable=import-outside-toplevel
        if run_protoc(opts) != 0:
            _die('Failed generation of proto files')
    except ImportError:
        _die('Package grpcio-tools isn\'t installed')


def _build_project():
    """Download and build boltlight dependencies and shell completions."""
    _download_lnd_deps()
    opts = [
        '--proto_path=.', '--python_out=.', '--grpc_python_out=.',
        path.sep.join([B_DIR, PROTO])
    ]
    _gen_proto(opts)
    with finput(files=(path.sep.join([B_DIR, 'walletunlocker.proto'])),
                inplace=True) as f:
        for line in f:
            if line.startswith('import'):
                print('import "boltlight/rpc.proto";', end='')
            else:
                print(line, end='')
    proto_include = resource_filename('grpc_tools', '_proto')
    for lnd_proto in LND_PROTOS:
        opts = [
            __file__, '--proto_path=.', '--proto_path=' + B_DIR,
            '--proto_path=' + proto_include, '--python_out=.',
            '--grpc_python_out=.',
            path.sep.join([B_DIR, lnd_proto])
        ]
        _gen_proto(opts)
    _try_rm(path.sep.join([B_DIR, GOOGLE]))


def _gen_cli_completion():
    """Generate completion scripts for blink.

    Blink's python entrypoint is required: if it's not in PATH, create it.
    To generate completion scripts blink.py must be imported, hence it's
    necessary to add eggs of external packages imported by it.
    """
    cli_in_path = bool(which(CLI_NAME))
    if not cli_in_path:
        maker = ScriptMaker(B_DIR, '.')
        maker.variants = set(('', ))
        maker.make_multiple((CLI_ENTRY, ))
        buf = None
        with open(CLI_NAME, 'r') as f:
            buf = f.readlines()
        add_egg = "spath.extend(egg)"
        get_egg = "egg = glob(path.join(getcwd(), '.eggs/{}-*.egg'))"
        lines = [
            "from sys import path as spath",
            "from glob import glob",
            "from os import getcwd, path",
            get_egg.format('click'),
            add_egg,
            get_egg.format('protobuf'),
            add_egg,
            get_egg.format('six'),
            add_egg,
            get_egg.format('grpcio'),
            add_egg,
        ]
        for idx, _ in enumerate(lines):
            lines[idx] = lines[idx] + linesep
        with open(CLI_NAME, 'w') as out:
            inserted = False
            for bufline in buf:
                if not bufline.startswith('#') and not inserted:
                    out.writelines(lines)
                    inserted = True
                out.write(bufline)
    _gen_shell_completion('bash', cli_in_path)
    _gen_shell_completion('zsh', cli_in_path)
    if not cli_in_path:
        _try_rm(CLI_NAME)


class Clean(clean):
    """Clean up generated and downloaded files."""
    def run(self):
        """Override default behavior."""
        for (dirpath, _dirnames, filenames) in walk('.'):
            _try_rm(path.sep.join([dirpath, '__pycache__']))
            for filename in filenames:
                filepath = path.join(dirpath, filename)
                for suffix in CLEANUP_SUFFIXES:
                    if filepath.endswith(suffix):
                        print(f'Removing file: "{filepath}"')
                        remove(filepath)
        for shell in SHELLS:
            _try_rm(path.sep.join([E_DIR, COMPLETION_SCRIPTS[shell]]))
        for report in Path(R_DIR).glob('*.report'):
            _try_rm(report.as_posix())
        _try_rm(path.sep.join([B_DIR, GAPIS_MASTER]))
        _try_rm(path.sep.join([B_DIR, GAPIS_ZIP]))
        _try_rm(path.sep.join([B_DIR, GOOGLE]))
        for lnd_proto in LND_PROTOS:
            _try_rm(path.sep.join([B_DIR, lnd_proto]))
        _try_rm(CLI_NAME)
        _try_rm('dist')
        _try_rm('.eggs')
        _try_rm('.coverage')
        _try_rm(B_DIR + '.egg-info')
        _try_rm('.pytest_cache')
        clean.run(self)


class BuildPy(build_py):
    """Build Python source."""
    def run(self):
        """Override default behavior."""
        _build_project()
        _gen_cli_completion()
        build_py.run(self)


class Develop(develop):
    """Define installation in development mode."""
    def run(self):
        """Override default behavior."""
        _build_project()
        develop.run(self)
        _gen_cli_completion()


class Lint(Command):
    """Lint code."""

    description = 'lint code with pycodestyle and pylint after in-place build'

    user_options = [
        ('pylint-rcfile=', None, 'path to pylint RC file'),
        ('pylint-format=', None, 'output format'),
    ]

    def initialize_options(self):
        """Override default behavior."""
        self.pylint_rcfile = ''
        self.pylint_format = ''

    def finalize_options(self):
        """Override default behavior."""
        if self.pylint_rcfile:
            assert path.exists(self.pylint_rcfile), (
                'Pylint RC file {self.pylint_rcfile} does not exist')
        else:
            self.pylint_rcfile = '.pylintrc'

    def run(self):
        """Override default behavior."""
        from pycodestyle import StyleGuide
        from pylint.lint import Run as PylintRun
        _build_project()
        TestCommand.install_dists(self.distribution)
        makedirs(R_DIR, exist_ok=True)
        print('Running pycodestyle')
        report = ''
        style = StyleGuide(paths=[PKG_NAME],
                           quiet=False,
                           exclude=PYCODESTYLE_EXCLUDE)
        try:
            with StringIO() as buf:
                with redirect_stdout(buf):
                    style.check_files()
                report = buf.getvalue()
            dest = path.join(R_DIR, 'pycodestyle.report')
            with open(dest, 'w') as f:
                f.write(report)
        except OSError:
            print('Failed')
        print('Running pylint')
        report = ''
        PYLINT_ARGS.insert(0, '--rcfile=' + self.pylint_rcfile)
        if self.pylint_format:
            PYLINT_ARGS.insert(1, f'--output-format={self.pylint_format}')
        try:
            with StringIO() as buf:
                with redirect_stdout(buf):
                    PylintRun(PYLINT_ARGS, do_exit=False)
                report = buf.getvalue()
            dest = path.join(R_DIR, 'pylint.report')
            with open(dest, 'w') as f:
                f.write(report)
        except OSError:
            print('Failed')


class Sdist(sdist):
    """Create source distribution."""
    def run(self):
        """Override default behavior."""
        _build_project()
        _gen_cli_completion()
        sdist.run(self)


if __name__ == "__main__":
    __version__ = getattr(import_module(B_DIR), '__version__')
    PIP_NAME = getattr(import_module(B_DIR + '.settings'), 'PIP_NAME')
    PKG_NAME = getattr(import_module(B_DIR + '.settings'), 'PKG_NAME')
    # documentation
    LONG_DESC = ''
    with open('README.md', encoding='utf-8') as readme:
        LONG_DESC = readme.read()
    setup(
        name=PIP_NAME,
        version=__version__,
        description='The Lightning Network node wrapper',
        long_description=LONG_DESC,
        long_description_content_type='text/markdown',
        classifiers=[
            'Development Status :: 4 - Beta',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: GNU Affero General Public License v3 '
            'or later (AGPLv3+)',
            'Natural Language :: English',
            'Operating System :: MacOS',
            'Operating System :: POSIX :: Linux',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'Programming Language :: Python :: 3.9',
            'Topic :: Other/Nonlisted Topic',
        ],
        keywords='boltlight ln node lightning network bitcoin blink wrapper',
        url='https://gitlab.com/hashbeam/boltlight',
        author='hashbeam',
        author_email='hashbeam@protonmail.com',
        license='AGPLv3',
        packages=[B_DIR, MIGRATIONS_DIR, MGR_VERSIONS_DIR, U_DIR],
        include_package_data=True,
        package_data={
            B_DIR: ['migrations/alembic.ini', PROTO],
        },
        data_files=[
            (f'share/doc/{PKG_NAME}/{E_DIR}', EXAMPLES),
            (f'share/doc/{PKG_NAME}', DOC),
        ],
        python_requires='>=3.7',
        install_requires=RUNTIME_DEPS,
        setup_requires=SETUP_DEPS,
        entry_points={
            'console_scripts': [
                CLI_ENTRY,
                f'boltlight = {B_DIR}.boltlight:start',
                f'boltlight-pairing = {B_DIR}.pairing:start',
                f'boltlight-secure = {B_DIR}.secure:secure',
            ]
        },
        cmdclass={
            'build_py': BuildPy,
            'clean': Clean,
            'develop': Develop,
            'lint': Lint,
            'sdist': Sdist,
        })
