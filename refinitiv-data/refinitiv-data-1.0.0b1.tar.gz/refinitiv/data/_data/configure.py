import asyncio
import atexit
import json
import os
import re
from json.decoder import WHITESPACE
from typing import Any, Optional

import config as ext_config_mod  # noqa
import nest_asyncio
from eventemitter import EventEmitter
from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer

from .tools._common import get_from_path


def _enable_watch():
    global _observer
    _observer = Observer()
    _event_handler = _RDPConfigChangedHandler(patterns=_config_files_paths)
    _dir_names = {os.path.dirname(f) for f in _config_files_paths}
    [_observer.schedule(_event_handler, dirname) for dirname in _dir_names]
    _observer.start()

    atexit.register(_disable_watch)


def _disable_watch():
    if _observer:
        _observer.stop()
        _observer.join()


def _dispose():
    _disable_watch()
    config.remove_all_listeners()


def _load_config_from_file(filepath):
    _configs = _create_configs([filepath] + _config_files_paths)
    _new_config = ext_config_mod.ConfigurationSet(*_configs)
    config.configs = _new_config.configs


def _get_filepath(rootdir, filename):
    if rootdir and filename:
        path = os.path.join(rootdir, filename)
        return path


_SUBS_PATTERN = re.compile(r".*?\${(\w+(-\w+)*(_\w+)*(:\w+)*)}.*?")


def _process_match(value, match, root):
    match = match or []
    for g in match:
        path = g[0]
        old = f"${{{path}}}"
        new = get_from_path(root, path, ":")
        new = None if isinstance(new, list) else new
        value = value.replace(old, new or old)
    return value


def _substitute_values(data, root=None):
    if not data:
        return data

    for k, v in data.items():
        if hasattr(v, "get"):
            _substitute_values(v, root)
        elif isinstance(v, str):
            match = _SUBS_PATTERN.findall(v)
            v = _process_match(v, match, root)
            data[k] = v
    return data


def _read_config_file(path):
    try:
        with open(path, "r") as f:
            data = json.load(f, cls=_JSONDecoder)
    except Exception:
        return {}

    return _substitute_values(data, data)


def _create_configs(files_paths):
    config_from_dict = ext_config_mod.config_from_dict
    dicts = [_read_config_file(f) for f in files_paths]
    configs = [config_from_dict(d) for d in dicts]
    return configs


def _create_rdpconfig(files_paths):
    if isinstance(files_paths, str):
        files_paths = [files_paths]
    configs = _create_configs(files_paths)
    return _RDPConfig(*configs)


class ConfigEvent:
    UPDATE = "update"


class _RDPConfigChangedHandler(PatternMatchingEventHandler):
    def on_any_event(self, event):
        configs = _create_configs(_config_files_paths)
        _new_config = ext_config_mod.ConfigurationSet(*configs)
        if _new_config.as_dict() != config.as_dict():
            config.configs = _new_config.configs
            try:
                config.emit(ConfigEvent.UPDATE)
            except Exception:
                pass


class _JSONDecoder(json.JSONDecoder):
    _ENV_SUBS_PATTERN = re.compile(r".*?\${(\w+)}.*?")

    def decode(self, s, _w=WHITESPACE.match):
        match = self._ENV_SUBS_PATTERN.findall(s)
        if match:
            for g in match:
                s = s.replace(f"${{{g}}}", os.environ.get(g, g))
            s = s.replace("\\", "\\\\")
        return super().decode(s, _w)


class _keys(object):
    endpoints = "endpoints"
    log_level = "logs.level"
    log_filename = "logs.transports.file.name"
    log_file_enabled = "logs.transports.file.enabled"
    log_console_enabled = "logs.transports.console.enabled"
    log_file_size = "logs.transports.file.size"
    log_filter = "logs.filter"
    log_max_files = "logs.transports.file.maxFiles"
    log_interval = "logs.transports.file.interval"
    watch_enabled = "config-change-notifications-enabled"

    http_request_timeout = "http.request-timeout"
    http_auto_retry_config = "http.auto-retry"

    desktop_sessions = "sessions.desktop"

    @staticmethod
    def desktop_session(session_name):
        return "sessions.desktop.%s" % session_name

    @staticmethod
    def desktop_base_uri(session_name):
        return "sessions.desktop.%s.base-url" % session_name

    @staticmethod
    def desktop_platform_paths(session_name):
        return "sessions.desktop.%s.platform-paths" % session_name

    @staticmethod
    def desktop_handshake_url(session_name):
        return "sessions.desktop.%s.handshake-url" % session_name

    @staticmethod
    def desktop_endpoints(session_name):
        return "sessions.desktop.%s.endpoints" % session_name

    platform_sessions = "sessions.platform"
    platform_session_default_server_mode = (
        "sessions.platform.default-session.server-mode"
    )

    @staticmethod
    def platform_session(session_name):
        return "sessions.platform.%s" % session_name

    @staticmethod
    def platform_endpoints(session_name):
        return "sessions.platform.%s.endpoints" % session_name

    @staticmethod
    def platform_base_uri(session_name):
        return "sessions.platform.%s.base-url" % session_name

    @staticmethod
    def platform_auth_uri(session_name):
        return "sessions.platform.%s.auth.url" % session_name

    @staticmethod
    def platform_token_uri(session_name):
        return "sessions.platform.%s.auth.token" % session_name

    @staticmethod
    def platform_auto_reconnect(session_name):
        return "sessions.platform.%s.auto-reconnect" % session_name

    @staticmethod
    def platform_server_mode(session_name):
        return "sessions.platform.%s.server-mode" % session_name

    @staticmethod
    def platform_realtime_distribution_system(session_name):
        return "sessions.platform.%s.realtime-distribution-system" % session_name

    stream_connects = "streaming.connections"

    @staticmethod
    def stream_connects_locations(session_name):
        return "streaming.connections.%s.locations" % session_name

    @staticmethod
    def stream_connects_type(session_name):
        return "streaming.connections.%s.type" % session_name

    @staticmethod
    def stream_connects_format(session_name):
        return "streaming.connections.%s.format" % session_name


class _RDPConfig(ext_config_mod.ConfigurationSet):
    keys = _keys

    def __init__(self, *configs):
        super().__init__(*configs)

        try:
            asyncio.get_event_loop()
        except RuntimeError:
            asyncio.set_event_loop(asyncio.new_event_loop())

        nest_asyncio.apply(asyncio.get_event_loop())

        self._emitter = EventEmitter()
        setattr(self, "on", self._emitter.on)
        setattr(self, "remove_listener", self._emitter.remove_listener)
        setattr(self, "remove_all_listeners", self._emitter.remove_all_listeners)
        setattr(self, "emit", self._emitter.emit)
        setattr(self, "count", self._emitter.count)
        setattr(self, "listeners", self._emitter.listeners)

    def set_param(self, param: str, value: Any, auto_create: bool = False) -> None:
        """
        Set param to the config.

        Parameters
        ----------
            param: str
                Parameter name.

            value: Any
                Parameter value.

            auto_create: bool
                Default value: False. We use auto_create to create new field in config

        Raises
        ----------
        Exception
            Raise exception if param name is not type 'str' .
        """
        if not isinstance(param, str):
            raise TypeError("Invalid type of parameter name, should be string")

        if not auto_create and not self._has_param(param):
            raise ValueError(
                f"'{param}' is not defined in config. "
                f"To create new parameter please use 'auto_create' property."
            )

        self[param] = value

    def _has_param(self, param: str):
        return param in self

    def get_param(self, param: str) -> Any:
        """
        Get param to the config.

        Parameters
        ----------
            param: str
                Parameter name.

        Raises
        ----------
        Exception
            Raise exception if config doesn't has param.
        """

        try:
            return self[param]
        except KeyError:
            raise AttributeError(f"Config object doesn't has '{param}' attribute")

    def _set_config_index(
        self, index: int, config_: ext_config_mod.Configuration
    ) -> None:
        """
        Set config by using index.
        This method is using for overriding default config.

        Parameters
        ----------
            index: int
                Parameter name.
            config_: Configuration
                Config object
        """
        if config_ is None:
            self._configs.pop(index)

        else:
            self._configs.insert(index, config_)


# ---------------------------------------------------------------------------
#   Initialize config
# ---------------------------------------------------------------------------

_RD_LIB_CONFIG_PATH = "RD_LIB_CONFIG_PATH"

_RDPLIB_ENV_DIR = "RDPLIB_ENV_DIR"

_default_config_file_name = "refinitiv-data.config.json"

_custom_filepath = os.environ.get(_RD_LIB_CONFIG_PATH, "")

if _custom_filepath:
    _custom_filepath = os.path.join(_custom_filepath, _default_config_file_name)

_project_config_dir = os.environ.get(_RDPLIB_ENV_DIR) or os.getcwd()

_config_files_paths = [
    c
    for c in [
        # CONFIG PROVIDED BY USER
        _custom_filepath,
        # PROJECT_CONFIG_FILE
        _get_filepath(rootdir=_project_config_dir, filename=_default_config_file_name),
        # USER_CONFIG_FILE
        _get_filepath(
            rootdir=os.path.expanduser("~"), filename=_default_config_file_name
        ),
        # DEFAULT_CONFIG_FILE
        _get_filepath(
            rootdir=os.path.dirname(__file__),
            filename=_default_config_file_name,
        ),
    ]
    if c
]

config = _create_rdpconfig(_config_files_paths)
# ---------------------------------------------------------------------------
#   Create public methods
# ---------------------------------------------------------------------------

keys = _keys

config.load = _load_config_from_file
load = _load_config_from_file
get = config.get
get_bool = config.get_bool
get_str = config.get_str
get_int = config.get_int

# ---------------------------------------------------------------------------
#   Initialize observer
# ---------------------------------------------------------------------------

_observer = None
_watch_enabled = config.get_bool(keys.watch_enabled)
if _watch_enabled:
    _enable_watch()

# ---------------------------------------------------------------------------
#   Defaults values from ./rdplibconfig.default.json
# ---------------------------------------------------------------------------
from .log import convert_log_level


class _defaults:
    http_request_timeout: Optional[str] = None
    log_level: Optional[int] = None
    platform_server_mode: Optional[bool] = None


_default_config = config.configs[len(config.configs) - 1]
defaults = _defaults()
defaults.http_request_timeout = _default_config.get(keys.http_request_timeout)
defaults.log_level = convert_log_level(_default_config.get(keys.log_level))
defaults.platform_server_mode = _default_config.get(
    keys.platform_session_default_server_mode
)
