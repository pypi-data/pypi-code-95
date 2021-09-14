import copy
import pprint
import logging
import json
from enum import Enum, unique
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    NamedTuple,
    Optional,
    Tuple,
)
from pathlib import Path

import appdirs

from solitude import TOOL_AUTHOR, TOOL_NAME
from solitude.cache import json_write_atomic


def get_existing_filepath(
    filename: str, valid_dirs: List[Path], allow_non_existing: bool = False
) -> Path:
    assert any(valid_dirs)
    full_path = Path()
    for valid_dir in valid_dirs:
        full_path = valid_dir / filename
        if full_path.is_file():
            return full_path
    if allow_non_existing:
        return full_path
    raise FileNotFoundError(
        f"Could not find a `{filename}` file in: {valid_dirs}"
    )


def resolve_core_filepaths(
    allow_non_existing: bool = False,
) -> Tuple[Path, Optional[Path], Path]:
    # Look for configuration and cache file:
    # 1) locally
    # 2) User home dir `user_config_dir` or `user_cache_dir`
    local_dir = Path(__file__).parent.parent.absolute()
    dirs = appdirs.AppDirs(appname=TOOL_NAME, appauthor=TOOL_AUTHOR)
    cache_fname = get_existing_filepath(
        filename="cache.json",
        valid_dirs=[local_dir, Path(dirs.user_cache_dir)],
        allow_non_existing=True,
    )
    assert cache_fname is not None
    config_filepath = get_existing_filepath(
        filename="config.json",
        valid_dirs=[local_dir, Path(dirs.user_config_dir)],
        allow_non_existing=allow_non_existing,
    )
    return cache_fname, config_filepath, local_dir


class Config(object):
    class Defaults(NamedTuple):
        username: str = "UNKNOWN"
        priority: str = "low"
        workers: int = 10
        cmdfiles: Tuple[Path, ...] = ()

    class SSHConfig(NamedTuple):
        server: str
        username: str
        password: str

    @unique
    class JobPriority(Enum):
        IDLE = "idle"
        LOW = "low"
        HIGH = "high"

    def __init__(self):
        self.logger = logging.getLogger(type(self).__name__)
        self.plugins = []
        self.defaults = Config.Defaults()
        self.ssh: Optional[
            Config.SSHConfig
        ] = None  # this is None if no valid ssh configuration is set
        self.config_path = None
        self.cache_path, self.config_path, _ = resolve_core_filepaths(
            allow_non_existing=True
        )
        self.load_config()

    def set_cmdfiles(self, cmdfiles: Iterable[Path]):
        self.defaults = Config.Defaults(
            username=self.defaults.username,
            priority=self.defaults.priority,
            workers=self.defaults.workers,
            cmdfiles=tuple(map(Path, cmdfiles)),
        )

    def _validate_property(
        self,
        settings: Dict,
        group: str,
        prop: str,
        test: Optional[Callable] = None,
        msg: str = "must be a string value.",
    ) -> bool:
        passed: bool
        try:
            passed = (
                test(settings[group][prop])
                if test is not None
                else isinstance(settings[group][prop], str)
            )
        except ValueError as ex:
            msg = str(ex)
            passed = False

        if not passed:
            self.logger.warning(
                f"`{group}` invalid value for `{prop}` was found "
                f"in config.\n{msg}"
            )
        return passed

    def _get_property_or_default(
        self,
        settings: Dict,
        group: str,
        prop: str,
        default: Any,
        test: Optional[Callable] = None,
        msg: str = "must be a string value.",
    ) -> Any:
        if self._validate_property(
            settings=settings, group=group, prop=prop, test=test, msg=msg
        ):
            return settings[group][prop]
        else:
            self.logger.warning(f"Resorting to default value: `{default}`.")
            return default

    def is_config_present(self) -> bool:
        return self.config_path.is_file()

    def is_ssh_configured(self) -> bool:
        return self.ssh is not None

    def to_json(self) -> Dict:
        return {
            "defaults": {
                "username": self.defaults.username,
                "workers": self.defaults.workers,
                "priority": self.defaults.priority,
                "cmdfiles": list(map(str, self.defaults.cmdfiles)),
            },
            "ssh": {
                "server": self.ssh.server,
                "username": self.ssh.username,
                "password": self.ssh.password,
            }
            if self.ssh is not None
            else None,
            "plugins": [],
        }

    def load_config(self):
        if self.is_config_present():
            with open(self.config_path, "r") as f:
                cfg = json.load(f)

            if "defaults" in cfg:
                defaults = cfg["defaults"]
                # import from json is a list by default, convert to tuple here
                if "cmdfiles" in defaults:
                    defaults["cmdfiles"] = tuple(defaults["cmdfiles"])
                # validate defaults
                self.defaults = Config.Defaults(
                    username=self._get_property_or_default(
                        settings=cfg,
                        group="defaults",
                        prop="username",
                        default=Config.Defaults.username,
                    ),
                    priority=self._get_property_or_default(
                        settings=cfg,
                        group="defaults",
                        prop="priority",
                        default=Config.Defaults.priority,
                        # ValueError raised if config string value not a member of JobPriority
                        test=lambda value: Config.JobPriority(value),
                    ),
                    workers=self._get_property_or_default(
                        settings=cfg,
                        group="defaults",
                        prop="workers",
                        default=Config.Defaults.workers,
                        test=lambda value: isinstance(value, int)
                        and value >= 0,
                        msg=f"must be an integer value >= 0.",
                    ),
                    cmdfiles=tuple(
                        map(
                            Path,
                            self._get_property_or_default(
                                settings=cfg,
                                group="defaults",
                                prop="cmdfiles",
                                default=Config.Defaults.cmdfiles,
                                test=lambda value: isinstance(value, tuple)
                                and all([isinstance(e, str) for e in value]),
                                msg=f"must be a list or tuple of strings.",
                            ),
                        )
                    ),
                )

            if "ssh" in cfg and all(
                [
                    e in cfg["ssh"]
                    and self._validate_property(
                        settings=cfg, group="ssh", prop=e,
                    )
                    for e in ["server", "username", "password"]
                ]
            ):
                ssh = cfg["ssh"]
                self.ssh = Config.SSHConfig(
                    server=ssh["server"],
                    username=ssh["username"],
                    password=ssh["password"],
                )
            else:
                self.ssh = None

            if (
                "plugins" in cfg
                and isinstance(cfg["plugins"], (list, tuple))
                and all([isinstance(e, str) for e in cfg["plugins"]])
            ):
                self.plugins = cfg["plugins"]
            else:
                self.plugins = []

    def display(self):
        """Display configuration, but obscure the ssh password"""
        cfgcopy = copy.deepcopy(self.to_json())
        if "ssh" in cfgcopy and "password" in cfgcopy["ssh"]:
            cfgcopy["ssh"]["password"] = "********"
        print("Configuration dump:")
        pprint.pprint(cfgcopy)

    def save(self):
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        json_write_atomic(fname=self.config_path, data=self.to_json())
