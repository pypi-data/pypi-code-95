# coding: utf-8

from __future__ import print_function, absolute_import, division, unicode_literals

_package_data = dict(
    full_package_name='release_info',
    version_info=(0, 2, 0),
    __version__='0.2.0',
    author='Anthon van der Neut',
    author_email='a.van.der.neut@ruamel.eu',
    description='automatically updated python release information',
    keywords='pypi statistics',
    entry_points='python_release_info=release_info.__main__:main',
    # entry_points=None,
    license='Copyright Ruamel bvba 2007-2020',
    since=2020,
    # status="α|β|stable",  # the package status on PyPI
    # data_files="",
    universal=True,
    install_requires=[],
    tox=dict(
        env='3',
    ),
    print_allowed=True,
)


version_info = _package_data['version_info']
__version__ = _package_data['__version__']


_cligen_data = """\
# all tags start with an uppercase char and can often be shortened to three and/or one
# characters. If a tag has multiple uppercase letter, only using the uppercase letters is a
# valid shortening
# Tags used:
# !Commandlineinterface, !Cli,
# !Option, !Opt, !O
# !PreSubparserOption, !PSO
# !Help, !H
# !Argument, !Arg
# !Module   # make subparser function calls imported from module
# !Instance # module.Class: assume subparser method calls on instance of Class imported from module
# !Action # either one of the actions in subdir _action (by stem of the file) or e.g. "store_action"
!Cli 0:
- !Instance release_info.release_info.ReleaseInfo
- !Option [verbose, v, !Help D|increase verbosity level, !Action count]
- !Option [dir, !Help 'base directory for all downloads and extraction']
- !Option [config, !Help directory for config file, default: '~/.config/python_release_info/']
- !O [force, !Action store_true, !Help 'force download (and extraction), normally skipped if already there']
- !O [type, !Help 'compiler type to work on: [cpython, tbd] (default: %(default)s)', default: 'cpython']
- update:
  - !Help download release_info.pon to config directory (if --dir specified also download new versions)
  - !Option [extract, !Help extract newly downloaded versions, !Action store_true]
  - !Option [build, b, !Help newly extracted versions]
  - !Option [delay, !H delay updating for DELAY days, type: int]
- current:
  - !Help list of current major.minor.micro versions
  - !Option [dd, !Action date, default: today, metavar: DATE, !Help 'show versions current on %(metavar)s (default: %(default)s)']
- pre:
  - !H list of not yet finalized releases
  - !Option [dd, !Action date, default: today, metavar: DATE, !Help 'show versions current on %(metavar)s (default: %(default)s)']
- download:
  - !H download/extract a particular version
  - !Opt [extract, !Action store_true, !Help extract downloaded tar file]
  - !Arg [version]
# - !Option [test, !Action store_true, !Help don't import version/packagedata from . (for testing cligen)]
# - !Option [all, !Action store_true, !Help build sdist and wheels for all platforms]
# - !Option [linux, !Action store_true, !Help build linux wheels using manylinux]
# - !Arg ['args', nargs: '*', !H you have to do this]
# - !Prolog 'Prolog for the parser'
# - !Epilog 'Epilog for the parser'
"""


def release_info():
    from .release_info import release_info as ri  # NOQA

    return ri
