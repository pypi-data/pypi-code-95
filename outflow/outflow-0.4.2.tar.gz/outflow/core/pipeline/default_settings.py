# -*- coding: utf-8 -*-
"""
Default Outflow settings. Override these with settings in the module pointed to
by the OUTFLOW_SETTINGS_MODULE environment variable.
"""
import os

from outflow.core.commands import RootCommand

ROOT_DIRECTORY = os.environ.get("PIPELINE_ROOT_DIRECTORY", None)

MAIN_DATABASE = "default"

PLUGINS = [
    "outflow.management",
]

BACKENDS = {
    "ray": "outflow.ray.backend",
}

ROOT_COMMAND_CLASS = RootCommand
