import itertools
import logging
import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any, Optional, Union

# @todo #0 Publish scpt on PyPI. The name is available.
#  https://packaging.python.org/tutorials/packaging-projects/
#  https://python-packaging.readthedocs.io/en/latest/minimal.html
#  https://github.com/maet3608/minimal-setup-py/blob/master/setup.py

# Suprisingly, there isn't an existing type definition combining path representations.
# REF: https://www.python.org/dev/peps/pep-0519/#provide-specific-type-hinting-support
#
# For users of this package, supplying a `bytes` value for a `CmdComponent` function
# parameter is taken to mean that that specific component should be excluded from ~
# expansion. To have all components, regardless of type, be excluded from ~ expansion,
# the `expand_tilde=False` keyword argument of the public functions should be used.
CmdComponent = Union[bytes, str, os.PathLike]


def _normalize_component(expand_tilde: bool, comp: CmdComponent) -> str:
    # Normalise CmdComponent to str, rather than Path. If we did Path, arguments to
    # commands that are not paths can become messed up, e.g. a URL "https://something"
    # becomes "https:/something" (note the single slash).
    if isinstance(comp, bytes):
        return comp.decode()
    elif isinstance(comp, str):
        return os.path.expanduser(comp) if expand_tilde else comp
    elif isinstance(comp, os.PathLike):
        fspath = comp.__fspath__()
        return os.path.expanduser(fspath) if expand_tilde else fspath


def _build_cmdline(
    expand_tilde: bool, name: CmdComponent, *args: CmdComponent
) -> list[str]:
    return [
        _normalize_component(expand_tilde, name),
        *[_normalize_component(expand_tilde, a) for a in args],
    ]


# ------------------------------------------------------------


def cd(path: CmdComponent, expand_tilde: bool = True) -> None:
    os.chdir(_normalize_component(expand_tilde, path))


def cmd(
    name: CmdComponent,
    *args: CmdComponent,
    expand_tilde: bool = True,
    **subprocess_check_call_kwargs: Any,
) -> None:
    subprocess.check_call(
        _build_cmdline(expand_tilde, name, *args), **subprocess_check_call_kwargs
    )


def output_of_cmd(
    name: CmdComponent,
    *args: CmdComponent,
    expand_tilde: bool = True,
    strip_trailing_newline: bool = True,
    **subprocess_run_kwargs: Any,
) -> str:
    completed_process = subprocess.run(
        _build_cmdline(expand_tilde, name, *args),
        check=True,
        capture_output=True,
        text=True,
        **subprocess_run_kwargs,
    )

    output = completed_process.stdout
    if strip_trailing_newline and output[-1:] == "\n":
        output = output[:-1]
    return output


# TWIN: `fileExistsInWdOrAnyParent` Bash function
def find_up(
    filename: CmdComponent, include_wd: bool = True, expand_tilde: bool = False
) -> Optional[Path]:
    basename = _normalize_component(expand_tilde, filename)
    wd = Path.cwd()
    up_dirs = itertools.chain([wd] if include_wd else [], wd.parents)
    for path in [directory / basename for directory in up_dirs]:
        if path.exists():
            return path
    else:
        return None


# ------------------------------------------------------------


def setup_logging(level_floor: int = logging.INFO) -> None:
    logging.basicConfig(
        format="%(levelname)s: %(message)s", level=level_floor, force=True
    )


def our_basename() -> str:
    return Path(sys.argv[0]).name


# ------------------------------------------------------------

# REF: https://docs.python.org/3.9/reference/datamodel.html#context-managers
# REF: https://docs.python.org/3.9/library/contextlib.html
class Caffeine:
    def __init__(self):
        system = platform.system()
        try:
            self.command_basename = {"Darwin": "caffeinate"}[system]
        except KeyError as e:
            raise NotImplementedError(
                f"Don't know a sleep avoidance command for system {system!r}"
            ) from e

    def __enter__(self):
        self.child = subprocess.Popen(self.command_basename)

    def __exit__(self, exc_type, exc_value, traceback):
        self.child.kill()
        os.waitpid(self.child.pid, 0)


__all__ = [
    "CmdComponent",
    "cd",
    "cmd",
    "output_of_cmd",
    "find_up",
    "setup_logging",
    "our_basename",
    "Caffeine",
]
