import re
from dataclasses import dataclass
from string import Template
from typing import List

import toml

LAMPIP_CONFIG_TOML_TEMPLATE = Template(
    """\
[lampip]
layername = "${layername}"
description = ""
pyversions = ["3.6", "3.7", "3.8"]

[lampip.shrink]
compile = true
compile_optimize_level = 2
remove_dist_info = true

[lampip.shrink.plotly]
remove_jupyterlab_plotly = true
remove_data_docs = true
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


@dataclass
class ShrinkPlotly:
    remove_jupyterlab_plotly: bool
    remove_data_docs: bool

    @classmethod
    def from_dict(cls, dct):
        return cls(
            remove_jupyterlab_plotly=dct.get("remove_jupyterlab_plotly", True),
            remove_data_docs=dct.get("remove_data_docs", True),
        )


@dataclass
class Shrink:
    compile: bool
    compile_optimize_level: int
    remove_dist_info: bool
    plotly: ShrinkPlotly

    @classmethod
    def from_dict(cls, dct):
        return cls(
            compile=dct.get("compile", True),
            compile_optimize_level=dct.get("compile_optimize_level", 2),
            remove_dist_info=dct.get("remove_dist_info", True),
            plotly=ShrinkPlotly.from_dict(dct.get("plotly", dict())),
        )


@dataclass
class Config:
    layername: str
    pyversions: List[str]
    description: str
    shrink: Shrink

    def __post_init__(self):
        validate_layername(self.layername)
        validate_pyversions(self.pyversions)

    @classmethod
    def from_dict(cls, dct):
        return cls(
            layername=dct["layername"],
            pyversions=dct["pyversions"],
            description=dct["description"],
            shrink=Shrink.from_dict(dct.get("shrink", dict())),
        )

    @classmethod
    def load_toml(cls, toml_file: str):
        with open(toml_file, "rt") as fp:
            contents = toml.load(fp)
        kargs = contents["lampip"]
        return cls.from_dict(kargs)
