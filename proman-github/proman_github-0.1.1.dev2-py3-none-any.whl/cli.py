# -*- coding: utf-8 -*-
# copyright: (c) 2020 by Jesse Johnson.
# license: MPL-2.0, see LICENSE for more details.
'''Arguments for inspection based CLI parser.'''

# import atexit
import json
import logging
import sys
from typing import Any

from . import get_package_manager

logger = logging.getLogger(__package__)

package_manager = get_package_manager()


def config() -> None:
    '''Manage distributions and global configuration.'''
    pass


def info(package: str, output: str = 'plain') -> None:
    '''Get package info.'''
    info = package_manager.info(package, output)
    print(json.dumps(info, indent=2))


def download(
    package: str, dest: str = '.', version: str = 'latest'
) -> None:
    '''Download packages.'''
    package_manager.download(package, dest, version=version)


def install(*packages: str, **options: Any) -> None:
    '''Install package and dependencies.

    Parameters
    ----------
    package: str
        package of package to be installed
    dev: bool
        add package as a development dependency
    prerelease: bool
        allow prerelease version of package
    optional: bool
        optional package that is not required
    platform: str
        restrict package to specific platform

    '''
    package_manager.install(*packages, **options)


def uninstall(*packages: str, **options: Any) -> None:
    '''Uninstall packages.'''
    package_manager.uninstall(*packages, **options)


def update(*packages: str, **options: Any) -> None:
    '''Install package and dependencies.

    Parameters
    ----------
    package: str
        package of package to be installed
    force: bool
        force changes

    '''
    package_manager.update(*packages, **options)


# def list(versions: bool = True) -> None:
#     '''List installed packages.'''
#     if versions:
#         for k in local_package.packages:
#             print(k.package.ljust(25), k.version.ljust(15), file=sys.stdout)
#     else:
#         print('\n'.join(local_package.package_packages), file=sys.stdout)


def search(*query: str, **options: str) -> None:
    '''Search PyPI for packages.

    Parameters
    ----------
    query: str
        Query(s) to search for projects.
    sort: str, optional
        Sort the results of query by either number of 'stars', 'forks',
        or 'updated'.
    order: str, optional
        Order the result either 'asc' or 'desc'.

    '''
    packages = package_manager.search(query=' '.join(query), **options)
    for package in packages:
        print(package, file=sys.stdout)
