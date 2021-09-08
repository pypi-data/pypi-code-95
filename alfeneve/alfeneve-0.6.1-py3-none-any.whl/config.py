# Copyright (c) 2019 Nick Douma <n.douma@nekoconeko.nl>
#
# This file is part of alfeneve .
#
# Licensed under the terms of the MIT license, see the
# LICENSE file in the root of the project.

from omniconf import setting, help_requested, show_usage, version_requested, \
    omniconf_load, config
from omniconf.types import separator_sequence
import sys


def get_version():
    from pbr.version import VersionInfo
    return VersionInfo("alfeneve").semantic_version()


VALID_MODES = ["categories", "properties", "whitelist", "transactions",
               "logs"]


def enum(valid_options):
    def validate(value):
        if value not in valid_options:
            raise RuntimeError(
                "Value is not valid, must be one of: {}"
                .format(", ".join(valid_options)))
        return value
    return validate


def load_properties_settings():
    setting("properties.category", default=None,
            help="Category of properties to lookup.")
    setting("properties.ids", _type=separator_sequence(","),
            help="IDs of individual properties to lookup, comma separated.")
    setting("properties.verbose", _type=bool, default=False,
            help="Show all values per property.")


def load_whitelist_settings():
    setting("whitelist.index", default=0, _type=int,
            help="Whitelist index to query.")


def load_logs_settings():
    setting("logs.since", _type=int,
            help="Retrieve logs since this ID.")
    setting("logs.count", _type=int, default=250,
            help="Retrieve a maximum amount of log lines "
                 "(default is 250 lines).")
    setting("logs.follow", _type=bool, default=False,
            help="Wait for new loglines.")


def load_settings():
    setting("alfen.endpoint", _type=str, required=True,
            help="API endpoint of an Alfen Eve charging point "
                 "(e.g. 'https://192.168.0.123').")
    setting("alfen.username", _type=str, required=True,
            help="Username for API (usually admin).")
    setting("alfen.password", _type=str, required=True,
            help="Password for API.")
    setting("alfen.certificate", _type=str, default=False,
            help="Path to SSL Certificate of the Alfen API endpoint "
                 "to use for SSL verification. By default no "
                 "verification is performed.")
    setting("mode", _type=enum(VALID_MODES), default="categories",
            help="Operation mode, must be one of: {}"
                 .format(", ".join(VALID_MODES)))

    if help_requested():
        load_properties_settings()
        load_whitelist_settings()
        load_logs_settings()
        show_usage(name="alfen-eve")

    if version_requested():
        print("alfen-eve {}".format(
            get_version().release_string()),
            file=sys.stderr)
        sys.exit(0)

    omniconf_load(autoconfigure_prefix="")

    if config("mode") == "properties":
        load_properties_settings()
    elif config("mode") == "whitelist":
        load_whitelist_settings()
    elif config("mode") == "logs":
        load_logs_settings()

    omniconf_load(autoconfigure_prefix="")
