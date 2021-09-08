"""Main profile execution."""
import sys
import textwrap
import typing as t
from collections import OrderedDict
from pathlib import Path

from dotty_dict import Dotty, dotty
from ruamel.yaml import YAML, parser, scanner

from .. import profiles
from .block import Block
from .utils import ProfileError, configure_logging

log = configure_logging(__name__)


def error(msg: str, exc_info: bool = False) -> None:
    """Helper function to log error and raise."""
    log.error(msg, exc_info=exc_info)
    raise ValueError(msg)


class Profile:  # pylint: disable=too-many-instance-attributes
    """Profile object.  Handles loading and execution."""

    def __init__(self, path: t.Union[Path, str], exit_on_error: bool = True) -> None:
        """Initialize profile from a path.

        Args:
            path (str): Path to the profile.
            exit_on_error (bool): Exit on errors or not.
        """
        self.errors: t.List[ProfileError] = []
        self.path = Path(path).resolve()
        # Local yaml loader/dumper
        self.yaml = YAML(typ="safe")
        # Raw profile as dict
        self.profile_raw: t.Dict[str, t.Any] = {}
        # Dictionary of <block_name> and their execution results
        self.block_results: t.Dict[str, bool] = {}
        # Dictionary of blocks and which profile they came from
        self.block_map: t.Dict[str, str] = {}
        # Deque of block objects
        self.blocks: OrderedDict = OrderedDict()
        # Map of include path to Profile object
        self.include_map: t.Dict[str, "Profile"] = {}
        try:
            with open(self.path, "r", encoding="utf-8") as fp:
                self.profile_raw = self.yaml.load(fp)
        except FileNotFoundError:
            error(f"Could not find profile at {self.path}")
        except (parser.ParserError, scanner.ScannerError):
            error("Could not load profile, is it valid YAML?", exc_info=True)
        # Profile name
        self.name: str = self.profile_raw.get("name", "")
        # List of includes
        self.includes: t.List[str] = self.profile_raw.get("includes", [])
        if not self.name:
            self.errors.append(ProfileError(None, "Profile must have a name"))
        # Handle includes
        for include in self.profile_raw.get("includes", []):
            errs = self.resolve_include(include)
            if errs:
                self.errors.extend(errs)
        # Handle blocks
        for block_raw in self.profile_raw.get("profile", []):
            block, errs = Block.from_dict(block_raw)
            # `block` will be None, skip it.
            if errs:
                self.errors.extend(
                    [e.add_component(f"profile ({self.name})") for e in errs]
                )
                continue
            self.handle_block(block, "local")  # type: ignore
        if exit_on_error:
            self.report_errs_and_exit()

    def report_errs_and_exit(self) -> None:
        """Print errors and exit."""
        if self.errors:
            msg = (
                "The following errors were found when loading the profile at "
                f"{self.path}:\n"
            )
            for err in self.errors:
                msg += textwrap.indent(f"- {err}\n\n", "  ")
            log.error(msg)
            sys.exit(1)

    def handle_block(self, block: Block, prof_name: str) -> None:
        """Handle a given block.

        * Add block to self.blocks, overriding the same name with newer (local)
            block
        * Add block to self.block_map with given profile name.
        * Add block to self.block_results with default result of False.

        Args:
            block (Block): block to handle.
            prof_name (str): Name of profile block came from.
        """
        if block.name in self.block_map:
            defined_profile = self.block_map[block.name]
            log.info(
                f"Found duplicate block {block.name} defined in  {prof_name} "
                f"replacing existing block defined in {defined_profile}"
            )

        self.block_map[block.name] = prof_name
        # Set all initial result to false
        self.block_results[block.name] = False
        # Populate block
        self.blocks[block.name] = block

    def resolve_include(self, include: str) -> t.List[ProfileError]:
        """Add included rules.

        Args:
            include (str): Name of profile to include
        """
        errors = []
        profile = self.__class__(profiles.get_profile(include), exit_on_error=False)
        if profile.errors:
            errors.extend(
                [e.add_component(f"profile ({self.name}") for e in profile.errors]
            )
        prof_name = profile.name
        if prof_name in self.include_map:
            errors.append(
                ProfileError(
                    prof_name,
                    "Profile is already included.  Profile names must be unique.",
                )
            )
            return errors
        self.include_map[prof_name] = profile
        for _, block in profile.blocks.items():
            self.handle_block(block, prof_name)
        return errors

    def evaluate(self, i_dict: t.Dict) -> t.Tuple[bool, Dotty]:
        """Evaluate the profile.

        Args:
            i_dict (t.Dict): Input dictionary

        Raises:
            ValueError: If a depends_on cannot be resolved.

        Returns:
            bool: True if any block successfully executed, False otherwise.
            Dotty: Possibly updated metadata

        """
        dotty_mods: Dotty = dotty(i_dict)

        for name, block in self.blocks.items():
            # Decide whether or not block should execute
            should_execute = True
            for depends in block.depends_on:
                try:
                    if not self.block_results[depends]:
                        should_execute = False
                        break
                except KeyError as e:
                    raise ValueError(
                        f"Block {name} depends on an unknown block {depends}"
                    ) from e
            # Execute block and save result
            if should_execute:
                res = block.evaluate(dotty_mods)
                self.block_results[name] = res
        executed: bool = any(self.block_results.values())
        return executed, dotty_mods

    def __repr__(self) -> str:
        """String representation."""
        obj_repr = f"Profile: {self.name}\n\nBlocks:\n" + textwrap.indent(
            "\n".join([repr(block) for _, block in self.blocks.items()]), "\t"
        )
        return obj_repr

    def to_dict(self) -> t.Dict:
        """Dump profile as a dictionary."""
        return {
            "name": self.name,
            "includes": self.includes,
            "profile": [
                block.to_dict()
                for name, block in self.blocks.items()
                if self.block_map[name] == "local"
            ],
        }

    def to_yaml(self, path: Path) -> None:
        """Dump `self.profile_raw` to yaml."""
        yaml_dumper = YAML(typ="rt")
        if not path.exists():
            path.touch()
        with open(path, "w", encoding="utf-8") as fp:
            yaml_dumper.dump(self.to_dict(), fp)
