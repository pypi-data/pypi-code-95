import os
import re
from pathlib import Path
from shutil import copyfile
from typing import Dict, Union, List, Match

import yaml
from fontawesome import icons
from i3ipc.aio import Con
from xdg import BaseDirectory

POSSIBLE_SWAY_CONFIG_PATHS = ['sway', 'i3']

CONFIG_FILE_NAME = 'sdn-config.yaml'

DEFAULT_DELIMITER = "|"
DEFAULT_DEFAULT_ICON = "dot-circle"

WINDOW_IDENTIFIERS = ('name', 'window_title', 'window_instance', 'window_class')

class ConfigException(Exception):
    pass

class RuntimeConfigException(Exception):
    pass


class ClientConfig:
    def __init__(self, key: str, data: Union[str, Dict]):
        self.key = key
        self.extra = None
        if type(data) == str:
            raw_icon = data
        elif type(data) == dict:
            raw_icon = data['icon']
            self.extra = data.get('extra', None)
            if type(self.extra) != str:
                raise ConfigException(f'clients/{key}/extra: invalid entity {self.extra}')
        else:
            raise ConfigException(f'clients/{key}: invalid entity {data}')

        self.icon = icons.get(raw_icon, raw_icon)

    def match(self, leaf: Con):
        for identifier in WINDOW_IDENTIFIERS:
            name = getattr(leaf, identifier, None)
            if name is None:
                continue
            match = re.match(self.key, name, re.IGNORECASE)
            if match:
                return match

    def get_symbol(self, leaf: Con, match: Match[str]):
        return Symbol(self, leaf, match)


class Symbol:
    def __init__(self, conf: ClientConfig, leaf: Con, match: Match[str]):
        self.conf = conf
        self.leaf = leaf
        self.match = match

        self.icon = self.format_str(self.conf.icon)
        self.extra = self.format_str(self.conf.extra) if self.conf.extra else None

    def format_str(self, value: str):
        d = {k: getattr(self.leaf, k, None) for k in WINDOW_IDENTIFIERS}
        try:
            return value.format(*self.match.groups(), **d)
        except IndexError:
            raise RuntimeConfigException(f"error formatting {value} with numbered values {self.match.groups()} and named values {d}")

    def get(self, workspaces_symbols: List[List["Symbol"]]):
        if self.extra is not None:
            for symbols in workspaces_symbols:
                for symbol in symbols:
                    if symbol.icon == self.icon:
                        return f"{self.icon} {self.extra}"
        return self.icon


class Config:
    _client_configs: Dict[str, ClientConfig] = {}
    _delimiter: str = "|"
    _last_modified: float = None

    def __init__(self, use_default=False):
        self.config_location = Config._find_config() if not use_default else Config._default_config_path()
        print(f"Using config file at {self.config_location}")

    def _load(self):
        if os.path.getmtime(self.config_location) != self._last_modified:
            with open(self.config_location, 'r') as f:
                data = yaml.safe_load(f)
            self._last_modified = os.path.getmtime(self.config_location)

            self._client_configs = {k: ClientConfig(k, v) for k, v in data.get('clients', {}).items()}
            self._delimiter = data.get('deliminator', DEFAULT_DELIMITER)
            self._default_icon = data.get('default_icon', DEFAULT_DEFAULT_ICON)
            self._default_icon = icons.get(self._default_icon, self._default_icon)

    @property
    def client_configs(self):
        self._load()
        return self._client_configs

    @property
    def delimiter(self):
        self._load()
        return self._delimiter

    @property
    def default_icon(self):
        self._load()
        return self._default_icon

    @staticmethod
    def _find_config():
        for possible_path in [pp.joinpath(CONFIG_FILE_NAME) for pp in Config._find_sway_folders()]:
            if possible_path.exists():
                return possible_path
        return Config._create_config(Config._find_sway_folders()[0].joinpath(CONFIG_FILE_NAME))

    @staticmethod
    def _find_sway_folders():
        config_base = Path(BaseDirectory.xdg_config_home)
        possible_paths = [config_base.joinpath(pp) for pp in POSSIBLE_SWAY_CONFIG_PATHS]
        return [pp for pp in possible_paths if pp.exists()]

    @staticmethod
    def _create_config(config_location: Path):
        print(f"Creating default config file at {config_location}")
        copyfile(Config._default_config_path(), config_location)
        return config_location

    @staticmethod
    def _default_config_path():
        return Path(os.path.realpath(__file__)).parent.joinpath('default.yaml')
