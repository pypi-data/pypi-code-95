#!/usr/bin/env python3
# -*- coding: utf-8; mode: python; -*-
# Copyright © 2020-2021 Pradyumna Paranjape
#
# This file is part of pspvis.
#
# pspvis is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pspvis is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with pspvis. If not, see <https://www.gnu.org/licenses/>.
#
"""
read configuration file
"""

import configparser
from pathlib import Path
from typing import Dict

import toml
import yaml

from pspvis.annotation import DataAnnot


def _load_yaml(config: Path) -> Dict[str, dict]:
    """
    Read configuration specified as a yaml file:
        - *.yml
        - *.yaml
    """
    with open(config, 'r') as rcfile:
        conf: Dict[str, dict] = yaml.safe_load(rcfile)
    if conf is None:  # pragma: no cover
        raise yaml.YAMLError
    return conf


def _load_ini(config: Path) -> Dict[str, dict]:
    """
    Read configuration supplied in
        - *.cfg
        - *.conf
    """
    parser = configparser.ConfigParser()
    parser.read(config)
    return {
        datacfg: dict(parser.items(datacfg))
        for datacfg in parser.sections()
    }  # pragma: no cover


def _load_toml(config: Path) -> Dict[str, dict]:
    """
    Read configuration supplied in ``pyproject.toml`` OR
        - *.toml
    """
    with open(config, 'r') as rcfile:
        conf: Dict[str, dict] = dict(toml.load(rcfile))
    if conf is None:  # pragma: no cover
        raise toml.TomlDecodeError
    return conf


def load_configuration(config: Path = None) -> DataAnnot:
    """
    load configuration file

    Args:
        conf: configuration file path (yaml, toml or ini file)
    """
    if config is None:
        return DataAnnot()
    if config.suffix in ('.yaml', '.yml'):
        conf = _load_yaml(config)
    elif config.suffix == 'toml':
        conf = _load_toml(config)
    elif config.suffix in ('.conf', '.cfg'):
        conf = _load_ini(config)
    else:
        # try each
        try:
            conf = _load_yaml(config)
        except yaml.YAMLError:
            try:
                conf = _load_toml(config)
            except toml.TomlDecodeError:
                conf = _load_ini(config)
    return DataAnnot(conf)
