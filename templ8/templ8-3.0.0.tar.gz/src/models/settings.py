import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Type, TypeVar

from ..models.cli import CLI
from ..utils.collections.dicts import (collapse_dict, key_is_true, merge_dicts,
                                       non_null_entries)
from ..utils.parsers.dataclasses import filter_into_dataclass
from ..utils.parsers.files import parse_yaml

T = TypeVar("T", bound="Settings")  # pylint: disable = C0103


@dataclass
class Settings:
    cwd: str
    output: str
    settings_file: str

    clear_top_level: bool = False
    logical_grouping: bool = False
    skip_core_templates: bool = False

    collection_sources: List[str] = field(default_factory=list)
    collections: List[str] = field(default_factory=list)

    includes: List[str] = field(default_factory=list)
    excludes: List[str] = field(default_factory=list)

    loader_paths: List[str] = field(default_factory=list)
    render_context: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def parse(cls: Type[T], cli: CLI) -> T:
        standard_paths = [".templ8.yml", ".template.yml"]

        if cli.settings_file is None:
            cwd = os.getcwd()
            settings_paths = [os.path.join(cwd, i) for i in standard_paths]
            settings_file = next(filter(os.path.exists, settings_paths), None)

        else:
            cwd = os.path.dirname(cli.settings_file)
            settings_file = cli.settings_file

        raw = merge_dicts(
            parse_yaml(settings_file) if settings_file is not None else {},
            non_null_entries(cli.__dict__),
            {"cwd": cwd, "settings_file": settings_file},
        )

        if "loader_paths" in raw:
            raw["loader_paths"] = [os.path.join(cwd, i) for i in raw["loader_paths"]]

        if "render_context" in raw and key_is_true(raw, "logical_grouping"):
            raw["render_context"] = collapse_dict(raw["render_context"])

        return filter_into_dataclass(cls, raw)
