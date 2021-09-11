#!/usr/bin/env python
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
preferences
"""

import configparser
import os
import sys
from pathlib import Path
from tkinter import ttk
from typing import Dict, List, Tuple

import toml
import yaml
from matplotlib import pyplot as plt
from ttkthemes import ThemedTk

from pspvis.data_types import PlotUserVars


def _parse_yaml(config: Path) -> Dict[str, dict]:
    """
    Read configuration specified as a yaml file:
        - .pspvisrc
        - preferences.yml
        - *.yml
    """

    with open(config, 'r') as rcfile:
        conf: Dict[str, dict] = yaml.safe_load(rcfile)
    if conf is None:  # pragma: no cover
        raise yaml.YAMLError
    return conf


def _parse_ini(config: Path, sub_section: bool = False) -> Dict[str, dict]:
    """
    Read configuration supplied in ``setup.cfg`` OR
        - *.cfg
        - *.conf
        - *.ini
    """
    parser = configparser.ConfigParser()
    parser.read(config)
    if sub_section:
        return {
            pspcfg.replace('pspvis.', ''): dict(parser.items(pspcfg))
            for pspcfg in parser.sections() if 'pspvis' in pspcfg
        }
    return {
        pspcfg: dict(parser.items(pspcfg))
        for pspcfg in parser.sections()
    }  # pragma: no cover


def _parse_toml(config: Path, sub_section: bool = False) -> Dict[str, dict]:
    """
    Read configuration supplied in ``pyproject.toml`` OR
        - *.toml
    """
    if sub_section:
        with open(config, 'r') as rcfile:
            conf: Dict[str, dict] = toml.load(rcfile).get('pspvis', {})
        return conf
    with open(config, 'r') as rcfile:
        conf: Dict[str, dict] = dict(toml.load(rcfile))
    if conf is None:  # pragma: no cover
        raise toml.TomlDecodeError
    return conf


def _parse_rc(config: Path) -> Dict[str, dict]:
    """
    Parse pspvisrc file

    Args:
        config: path to configuration file

    Returns:
        configuration sections

    Raises:
        BadMark: Bad configuration

    """
    try:
        # yaml configuration format
        return _parse_yaml(config)
    except yaml.YAMLError:
        try:
            # toml configuration format
            return _parse_toml(config)
        except toml.TomlDecodeError:
            try:
                # try generic config-parser
                return _parse_ini(config)
            except configparser.Error:
                pass
    return {}


def xdg_vars() -> Tuple[Path, Path]:
    """
    Platform-specific xdg-vars: config/data

    Returns:
        root config- (/etc) and user-config- ($XDG_CONFIG_HOME) directory
    """
    # environment
    if sys.platform.startswith('win'):  # pragma: no cover
        # windows
        user_home = Path(os.environ['USERPROFILE'])
        root_config = Path(os.environ['APPDATA'])
        xdg_config = Path(
            os.environ.get('LOCALAPPDATA', user_home / 'AppData/Local'))
    else:
        # assume POSIX
        user_home = Path(os.environ['HOME'])
        root_config = Path('/etc')
        xdg_config = Path(os.environ.get('XDG_CONFIG_HOME', user_home / '.config'))

    return root_config, xdg_config


def read_config(custom: os.PathLike = None) -> PlotUserVars:
    """
    Read pspvis configurations from various locations

    Args:
        custom: custom location for configuration

    Returns:
        configured ``PlotUserVars``

    Raises:
        BadMark- Bad configuration file format
    """

    # Preference of configurations *Most dominant first*
    config_heir: List[Path] = []

    # custom
    if custom is not None:
        if not Path(custom).is_file():
            raise FileNotFoundError(
                f'Custom configuration file: {custom} not found')
        config_heir.append(Path(custom))

    # environment variable
    pspvisrc_var = os.environ.get('PSPVISRC')
    if pspvisrc_var is not None:
        if not Path(pspvisrc_var).is_file():
            raise FileNotFoundError(
                f'PSPVISRC configuration file: {pspvisrc_var} not found')
        config_heir.append(Path(pspvisrc_var))

    # current working directory
    config_heir.append(Path('.').resolve() / '.pspvirc')

    root_config, xdg_config = xdg_vars()
    # standard locations
    for heir in xdg_config, root_config, Path(__file__).parent.parent:
        for ext in '.yml', '.yaml', '.toml', '.conf':
            config_heir.append((heir / 'pspvis/preferences').with_suffix(ext))

    # load configs from oldest ancestor to current directory
    conf = PlotUserVars()
    for config in reversed(config_heir):
        try:
            conf.update(_parse_rc(config))
        except (PermissionError, FileNotFoundError, IsADirectoryError):
            pass

    # initialize with config

    return conf


def write_config(conf: PlotUserVars):
    """
    write configuration to standard location in yaml format
    """
    _, xdg_var = xdg_vars()
    config_parent = xdg_var / 'pspvis'
    config_parent.mkdir(parents=True, exist_ok=True)
    auto_prefr = config_parent / 'preferences.yml'
    with open(auto_prefr, 'w') as pref_out:
        yaml.dump(conf.__dict__, pref_out)


def collect_themes() -> Dict[str, Dict[str, str]]:
    """
    Collect avail_themes from 'avail_themes' folder and mpl's API
    """
    avail_themes = {'ui': {'default': ''}, 'mpl': {'default': 'classic'}}

    temproot = ThemedTk()
    style = ttk.Style(temproot)
    temproot.destroy()
    for theme in style.theme_names():
        avail_themes['ui'][theme] = theme

    for theme in plt.style.available:
        avail_themes['mpl'][theme] = theme

    for theme in (Path(__file__).parent / 'avail_themes').glob('*.mplstyle'):
        avail_themes['mpl'][theme.stem] = str(theme)
    return avail_themes
