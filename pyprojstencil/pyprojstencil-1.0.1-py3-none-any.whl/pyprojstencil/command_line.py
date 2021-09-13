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
Command line inputs
"""

from argparse import ArgumentParser, RawDescriptionHelpFormatter
from pathlib import Path
from typing import Dict

from argcomplete import autocomplete

from pyprojstencil.configure import PyConfig, read_config
from pyprojstencil.errors import NoProjectNameError
from pyprojstencil.get_license import get_license


def project_path(project: str) -> Path:
    """
    Check whether parent exists

    Args:
        project: path of project

    Returns:
        resolved ``Path`` to project

    Raises:
        FileExistsError: project already exists
    """
    if Path(project).exists():
        raise FileExistsError(f'{project} already exists')
    return Path(project).resolve()


def filepath(location: str) -> Path:
    """
    Check whether the given location is a valid path to a file

    Args:
        location: Path to be validated

    Returns:
        ``Path`` for location

    Raises:
        FileNotFoundError: location is not an existing file
    """
    location_path = Path(location)
    if location_path.is_file():
        return location_path
    raise FileNotFoundError(f"{location} was not found")


def _cli() -> ArgumentParser:
    """
    Accept command line arguments
    """
    description = '''
    '''
    parser = ArgumentParser(description=description,
                            formatter_class=RawDescriptionHelpFormatter)
    parser.add_argument('-c',
                        '--config',
                        help='pre-defined configuration',
                        default=None,
                        type=filepath)
    parser.add_argument('-l',
                        '--license',
                        default='LGPLv3',
                        type=str,
                        help='License name or "custom" [default: LGPLv3]')
    parser.add_argument('-y',
                        '--year',
                        default=None,
                        type=str,
                        help='copyright period e.g. 2020-2021')
    parser.add_argument('-a',
                        '--author',
                        default=None,
                        type=str,
                        help='Name of author')
    parser.add_argument('-p',
                        '--python-exe',
                        default=None,
                        dest='pyversion',
                        type=str,
                        help='Python version in virtual environment [eg. 3.9]')
    parser.add_argument('project',
                        type=project_path,
                        help="Name of python project")
    autocomplete(parser)
    return parser


def cli() -> Dict[str, str]:
    """
    Command line arguments
    """
    parser = _cli()
    return vars(parser.parse_args())


def configure() -> PyConfig:
    """
    Set configuration variables

    Returns:
        Configuration variables object

    Raises:
        NoProjectNameError: project name missing
    """
    cli_inputs = cli()
    config = read_config(cli_inputs.get('config'))
    config.update(**cli_inputs)
    config.license, config.license_header = get_license(cli_inputs['license'])
    if config.author is None:
        raise NoProjectNameError
    if config.project is None:
        raise NoProjectNameError
    return config
