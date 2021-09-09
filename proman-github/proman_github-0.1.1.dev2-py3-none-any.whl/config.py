# -*- coding: utf-8 -*-
# copyright: (c) 2020 by Jesse Johnson.
# license: MPL-2.0, see LICENSE for more details.
'''Configuration for package manager.'''

import os
from dataclasses import dataclass, field
from typing import Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from proman_common.manifest import LockFile, SourceTreeFile

url_base = os.getenv('PROMAN_GITHUB_URL', 'https://api.github.com')


@dataclass
class ProjectPaths:
    '''Project directories.'''

    working_dir: str = os.getcwd()
    virtualenv_dir: Optional[str] = os.getenv('VIRTUAL_ENV', None)
    pyproject_path: str = field(init=False)
    lock_path: str = field(init=False)
    pypackages_dir: str = field(init=False)

    def __post_init__(self) -> None:
        '''Initialize python project.'''
        self.pyproject_path = os.path.join(self.working_dir, 'pyproject.toml')
        self.lock_path = os.path.join(self.working_dir, 'proman-lock.json')
        self.pypackages_dir = os.path.join(self.working_dir, '__pypackages__')
