#!/usr/bin/env python3
# -*- coding:utf-8; mode:python; -*-
#
# Copyright 2021 Pradyumna Paranjape
# This file is part of pyprojstencil.
#
# pyprojstencil is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pyprojstencil is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with pyprojstencil.  If not, see <https://www.gnu.org/licenses/>.
#
"""
Read yaml configuration
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Union

import yaml


def _default_config(
        config_file: Union[str, os.PathLike] = None) -> Optional[Path]:
    """
    Location of default configuration file

    Returns:
        path of default configuration file if found, else ``None``
    """
    if config_file is None:
        home_dir = os.environ.get('HOME')
        config_dir = os.environ.get('XDG_CONFIG_HOME')
        if config_dir is None:
            if home_dir is None:
                return
            config_dir = Path(home_dir).joinpath('.config')  # usually
        config_dir_path = Path(config_dir)
        if not config_dir_path.is_dir():
            # configuration directory does not exist
            if home_dir is None:
                return
            config_dir_path = Path(home_dir)
        config_file = config_dir_path.joinpath('ppstencil.yml')
    config_file = Path(config_file)
    if not config_file.is_file():
        return
    return config_file


class PyConfig():
    """
    Configuration for Python project stencil.
    Values for commonly declared variables in python projects.
    The author must add the rest by hand.

    Attributes:
        project: project name
        version: project version
        description: project description
        years: copyright years
        license: project license [LGPLv3]
        license_header: project license header [LGPLv3]
        pyversion: compatible python version
        author: author's displayed name
        uname: author's user name
        email: author's email
        githost: host [remote] website for git
        branch: git's initial branch [default: `pagan`]
        url: project's url
        keys: all class key names
    """
    def __init__(self, **kwargs):
        # TODO: setter for license
        self.project: Optional[Path] = None
        self.version: str = '0.0dev1'
        self.description: str = f'{self.project}'
        self.years: str = str(datetime.now().year)
        self.license: Optional[Path] = None
        self.license_header: str = (
            '#\n' + '# Contact the author(s) for License terms\n' + '#\n')
        self.pyversion: str = "3"
        self.author: str = os.environ.get('USER', 'AUTHOR')
        self.email: Optional[str] = None
        self.url: Optional[str] = None
        self._uname: Optional[str] = None
        self.githost: str = "gitlab"
        self.branch: str = "pagan"
        self.keys = ('license_header', 'description', 'pyversion', 'project',
                     'version', 'githost', 'license', 'author', 'email', 'url',
                     'uname', 'years')
        self.update(**kwargs)

    @property
    def uname(self) -> str:
        if self._uname:
            return self._uname
        return self.author.lower().replace(" ", "_")  # a bad default idea

    @uname.deleter
    def uname(self):
        self._uname = None

    @uname.setter
    def uname(self, value):
        self._uname = value

    def update(self, **kwargs):
        """
        Update key-value-pairs from kwargs if they are not defaults

        Args:
            **kwargs: key-value pairs that can update ``attributes``

                - rest are ignored

        """
        for key, value in kwargs.items():
            if value is not None:
                if key in self.keys:
                    if isinstance(value, int):
                        setattr(self, key, str(value))
                    else:
                        setattr(self, key, value)

    def __repr__(self) -> str:
        """
        Representation of object
        """
        output = ['']
        for key, value in self.__dict__.items():
            output.append(f"{key}: {value}")
        output.append('')
        return '\n    '.join(output)


def read_config(config_file: Union[os.PathLike, str] = None) -> PyConfig:
    """
    Read standard configuration for project
    """
    config_path = _default_config(config_file)
    if config_path is None:
        return PyConfig()
    with open(config_path) as std_cfg:
        config = PyConfig(**yaml.safe_load(std_cfg))
    return config
