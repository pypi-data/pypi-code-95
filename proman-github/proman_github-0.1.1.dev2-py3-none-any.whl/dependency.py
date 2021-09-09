# -*- coding: utf-8 -*-
# copyright: (c) 2020 by Jesse Johnson.
# license: MPL-2.0, see LICENSE for more details.
'''Resolve package dependencies.'''

import re
from typing import Any, Dict, Tuple, TYPE_CHECKING

# from packaging.specifiers import SpecifierSet
from proman_common.dependencies import DependencyBase

if TYPE_CHECKING:
    from github.GitReleaseAsset import GitReleaseAsset


class Dependency(DependencyBase):
    '''Manage dependency of a project.'''

    def __init__(
        self,
        asset: 'GitReleaseAsset',
        **options: Any,
    ) -> None:
        '''Initialize dependency.'''
        self._asset = asset
        self.__version = options.get('version', 'latest')
        self.__dev = options.get('dev', False)
        self.__platform = options.get('platform', None)
        self.__optional = options.get('optional', False)
        self.__prerelease = options.get('prerelease', False)

    def __getattr__(self, attr: str) -> Any:
        '''Provide proxy for distribution.'''
        return getattr(self._asset, attr)

    @staticmethod
    def __get_specifier(package: str) -> Tuple[str, str]:
        '''Get package name and version.'''
        regex = '^([a-zA-Z0-9][a-zA-Z0-9._-]*)([<!~=>].*)$'
        package_info = [x for x in re.split(regex, package) if x != '']
        name = package_info[0]
        if len(package_info) == 2:
            version = package_info[1]
        else:
            version = '*'
        return name, version

    @property
    def name(self) -> str:
        '''Get name.'''
        return self._asset.name

    @property
    def version(self) -> str:
        '''Get version.'''
        return self.__version

    @property
    def digests(self) -> Tuple[Dict[str, str]]:
        '''Get digests.'''
        return ({},)

    @property
    def url(self) -> str:
        '''Get url.'''
        return self._asset.url
