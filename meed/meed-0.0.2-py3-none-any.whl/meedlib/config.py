import logging
from configparser import ConfigParser
from os import environ, path, makedirs
from typing import *

from .terminal import header, required_property_input, property_input


class MeedConfigNotExists(FileNotFoundError):
    MESSAGE = "Could not load meed config, check configuration file exists and configuration profile is present"


class MeedConfig:
    REQUIRED_PROPERTIES = ["Output_File"]
    PROPERTIES = {
        "AWS_Profile": None,
        "Theme": "DarkGrey",
        "Stats": ["Happiness", "Confidence", "Frustration"],
        "Depth": 10,
        "Style": "Radio",
    }

    def __init__(self, profile: str or None = None):
        self.configuration_file_path = environ.get(
            "MEED_CONFIG_PATH",
            path.join(path.expanduser("~"), ".config", "meed", "config.ini"),
        )
        self.config = None
        self.profile_name = profile
        if profile:
            self.load_profile(profile)

    def load_profile(self, profile_name):
        config = ConfigParser()
        config.read(self.configuration_file_path)
        try:
            self.config = config[profile_name]
        except KeyError:
            logging.error(
                f"invalid profile '{profile_name}' for configuration '{self.configuration_file_path}'"
            )
            raise MeedConfigNotExists

    def terminal_list_profiles(self):
        header("Available meed profiles")
        for profile in self.get_profiles():
            print(" • " + profile)

    def terminal_create_new_profile(self):
        header("Setup new meed log profile")
        profile_name = required_property_input("Profile_Name")
        options = {
            prop: required_property_input(prop)
            for prop in MeedConfig.REQUIRED_PROPERTIES
        }
        for prop, default in MeedConfig.PROPERTIES.items():
            if type(default) is list:
                default = ",".join(default)
            val = property_input(prop, default)
            if type(default) is list and type(val) is str:
                options[prop] = val.strip()
            elif type(default) is int and type(val):
                options[prop] = str(val)
            elif val is None:
                continue
            else:
                options[prop] = val
        self._create_new_profile(profile_name=profile_name, options=options)

    def _create_new_profile(self, profile_name: str, options=None):
        if options is None:
            options = {}
        config = ConfigParser()
        config[profile_name] = {}
        for key, val in options.items():
            config[profile_name][key] = val

        makedirs(path.dirname(self.configuration_file_path), exist_ok=True)
        with open(self.configuration_file_path, "a+") as config_file:
            config.write(config_file)
        self.config = config

    def get_profiles(self) -> List[str]:
        if path.exists(self.configuration_file_path):
            config = ConfigParser()
            config.read(self.configuration_file_path)
            return config.sections()
        return []

    def __getitem__(self, item: str) -> Any:
        if item in MeedConfig.REQUIRED_PROPERTIES:
            return self.config[item]
        if item in MeedConfig.PROPERTIES:
            val = self.config.get(item, MeedConfig.PROPERTIES[item])
            if type(MeedConfig.PROPERTIES[item]) is list:
                val = val.split(",")
            elif type(MeedConfig.PROPERTIES[item]) is int:
                val = int(val)
            return val
