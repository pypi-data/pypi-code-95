"""Provides the code to load credmgr's configuration file `~/.credmgr.ini`."""
import configparser
import os
import sys
from pathlib import Path
from threading import Lock


class Config:
    _config = None
    _lock = Lock()

    @staticmethod
    def _appendFileName(dirname):
        return os.path.join(dirname, ".credmgr.ini")

    @classmethod
    def _loadConfig(cls):
        """Attempt to load settings from various .credmgr.ini files."""
        config = configparser.ConfigParser()
        rootDir = os.path.dirname(sys.modules[__name__].__file__)
        locations = [
            cls._appendFileName(rootDir),
            cls._appendFileName(Path.home()),
            ".credmgr.ini",
        ]
        config.read(locations)
        cls._config = config

    def __init__(self, configName, **kwargs):
        """Initialize a Config instance."""
        with Config._lock:
            if Config._config is None:
                self._loadConfig()

        self._settings = kwargs
        self.customSettings = dict(
            Config._config.items(configName),
            **{k.lower(): v for k, v in kwargs.items() if v},
        )
        self.server = self.apiToken = self.username = self.password = None

        self._initializeConfig()

    def _fetch(self, key, default=None):
        configFileValue = self.customSettings.pop(key.lower(), default)
        envOverride = os.getenv(f"credmgr_{key}")
        return envOverride or configFileValue

    def _initializeConfig(self):
        self.server = self._fetch("server")
        self.endpoint = self._fetch("endpoint")
        self.apiToken = self._fetch("apitoken")
        self.username = self._fetch("username")
        self.password = self._fetch("password")
        self.dateFormat = self._fetch("dateformat")
