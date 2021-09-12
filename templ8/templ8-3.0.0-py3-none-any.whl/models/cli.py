from argparse import ArgumentParser
from dataclasses import dataclass
from logging import DEBUG, INFO, WARNING
from typing import Any, Dict, List, Optional, Type, TypeVar

from .. import __version__
from ..utils.extensions.format_help import format_help
from ..utils.extensions.store_kv import StoreKV
from ..utils.parsers.dataclasses import pick_into_dataclass

T = TypeVar("T", bound="CLI")  # pylint: disable = C0103

parser = ArgumentParser(
    "templ8",
    description=f"Templ8 {__version__}",
)

format_help(parser)

parser.add_argument(
    "--output",
    help="output directory.",
    action="store",
)

parser.add_argument(
    "--settings-file",
    help="input file path.",
    action="store",
)

parser.add_argument(
    "--dry-run", help="don't make any changes.", action="store_true", default=False
)

parser.add_argument(
    "--silent", help="don't output any logs.", action="store_true", default=False
)

parser.add_argument(
    "--debug", help="output debug logs.", action="store_true", default=False
)

parser.add_argument(
    "--clear-top-level",
    help="remove top level files.",
    action="store_true",
    default=None,
)

parser.add_argument(
    "--logical-grouping",
    help="flatten render context.",
    action="store_true",
    default=None,
)

parser.add_argument(
    "--skip-core-templates",
    help="skip core templates.",
    action="store_true",
    default=None,
)

parser.add_argument(
    "--collection-sources",
    help="where to look for collections.",
    action="append",
)

parser.add_argument(
    "--collections",
    help="collection names.",
    action="append",
)

parser.add_argument(
    "--includes",
    help="path names to include.",
    action="append",
)

parser.add_argument(
    "--excludes",
    help="path names to exclude.",
    action="append",
)

parser.add_argument(
    "--loader-paths",
    help="where to look for Jinja includes.",
    action="append",
)

parser.add_argument(
    "--render-context",
    help="jinja context variables.",
    action=StoreKV,
)


@dataclass
class CLI:
    # Some properties are Optional since we want
    # to be able to detect when they are not set.

    output: Optional[str]
    settings_file: Optional[str]

    dry_run: bool
    silent: bool
    debug: bool

    clear_top_level: Optional[bool]
    logical_grouping: Optional[bool]
    skip_core_templates: Optional[bool]

    collection_sources: List[str]
    collections: List[str]

    includes: List[str]
    excludes: List[str]

    loader_paths: List[str]
    render_context: Dict[str, Any]

    @classmethod
    def parse(cls: Type[T]) -> T:
        return pick_into_dataclass(cls, parser.parse_args())

    @property
    def loglevel(self) -> int:
        if self.debug:
            return DEBUG

        if self.silent:
            return WARNING

        return INFO
