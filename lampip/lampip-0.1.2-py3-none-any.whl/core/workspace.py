import os
import os.path as op
import re
from string import Template
from typing import Sequence

import toml
from termcolor import cprint

from .package import make_package, upload_package

LAMPIP_CONFIG_TOML_TEMPLATE = Template(
    """\
[lampip.config]
layername = "${layername}"
description = ""
pyversions = ["3.8", "3.7", "3.6"]
"""
)


def validate_layername(layername):
    if not re.search(r"^[a-zA-Z0-9_-]+$", layername):
        raise ValueError(
            f"Invalid layername `{layername}`;"
            " The layer name can contain only letters, numbers, hyphens, and underscores."
        )
    if len(layername) > 64 - 5:
        raise ValueError(
            f"Invalid layername `{layername}';" " The maximum length is 59 characters."
        )


def validate_pyversions(pyversions):
    if len(pyversions) == 0:
        raise ValueError("Invalid pyversions; pyversions should not be empty.")
    if not set(pyversions) <= {"3.8", "3.7", "3.6"}:
        raise ValueError(
            f'Invalid pyversions {pyversions}; Supported pyversions are "3.6", "3.7", ".3.8" .'
        )


class LampipConfig:
    def __init__(self, layername: str, pyversions: Sequence[str], description: str):
        validate_layername(layername)
        validate_pyversions(pyversions)
        self.layername = layername
        self.pyversions = pyversions
        self.description = description

    def __repr__(self):
        return f"LampipConfig(layername={self.layername}, pyversions={self.pyversions})"

    @classmethod
    def load_toml(cls, toml_file: str):
        with open(toml_file, "rt") as fp:
            contents = toml.load(fp)
        kargs = contents["lampip"]["config"]
        return cls(**kargs)


class Workspace:
    def __init__(self, directory: str, layername: str):
        self.directory = directory
        self.layername = layername

    @classmethod
    def create_scaffold(cls, layername) -> "Workspace":
        """Create the scaffold to the specified directory

        Files
        - requirements.txt: empty file
        - lampip-config.toml

        """
        validate_layername(layername)
        directory = op.join(".", layername)
        if op.exists(directory):
            raise FileExistsError(f"{directory} already exists")
        cprint(f"Create the scaffold: {layername}", color="green")
        os.mkdir(directory)
        # requirements.txt: empty file
        with open(op.join(directory, "requirements.txt"), "wt") as fp:
            pass
        # lampip-config.toml
        with open(op.join(directory, "lampip-config.toml"), "wt") as fp:
            fp.write(LAMPIP_CONFIG_TOML_TEMPLATE.substitute(layername=layername))
        print(
            f"+ {op.join(directory, 'requirements.txt')}\n"
            f"+ {op.join(directory, 'lampip-confing.toml')}"
        )
        return cls(directory, layername)

    @classmethod
    def load_directory(cls, directory: str) -> "Workspace":
        os.chdir(directory)
        config = LampipConfig.load_toml(op.join(directory, "lampip-config.toml"))
        return cls(directory, config.layername)

    def deploy(self, upload_also=True):
        """Build and upload the lambda custom layer."""
        config = LampipConfig.load_toml(op.join(self.directory, "lampip-config.toml"))
        for ver in config.pyversions:
            make_package(config.layername, ver)
            if upload_also:
                upload_package(config.layername, ver, config.description)
