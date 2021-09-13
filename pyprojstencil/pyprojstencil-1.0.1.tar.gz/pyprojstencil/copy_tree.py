#!/usr/bin/env python3
# -*- coding:utf-8; mode:python; -*-
#
# Copyright 2021 Pradyumna Paranjape
# This file is part of pyprojstencil.
#
# pyprojstencil is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pyprojstencil is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with pyprojstencil.  If not, see <https://www.gnu.org/licenses/>.
#
"""
Deep copy the templates directory with modifications
"""

import os
import stat
from pathlib import Path

from pyprojstencil.common import edit_modify
from pyprojstencil.configure import PyConfig
from pyprojstencil.errors import MaxRecursion, TemplateMissingError


def _mod_exec(exec_file: os.PathLike) -> None:
    """
    Make file executable

    Args:
        exec_file: path of file to be made executable

    Returns:
        ``None``
    """
    st = os.stat(exec_file)
    os.chmod(exec_file, st.st_mode | stat.S_IEXEC)


def mod_exec(config: PyConfig) -> None:
    """
    make files in the directory "code-aid" executable
    """
    for exe_path in ("code-aid/init_venv.sh", "code-aid/install.sh",
                     "code-aid/coverage.sh", "code-aid/pypi.sh",
                     'code-aid/build_sphinx.sh',
                     config.project.name + "/__main__.py"):
        _mod_exec(config.project.joinpath(exe_path))


def tree_copy(config: PyConfig,
              source: os.PathLike,
              destin: os.PathLike,
              skip_deep: bool = False,
              stack: int = 0) -> bool:
    """
    Recursively copy file tree
    - Skips project-specific directories, if found:

      - .git
      - .venv

    - Nodes handling:

      - Directories are created
      - Links are interpreted and linked,
      - Files are modified-edit and written

    Args:
        config: pyprojstencil configuration
        source: Path to root of source-tree
        destin: Path to root of destination-tree (created if not found)

    Raises:
        TemplateMissingError: source could not be located
        MaxRecursion: Tree structure is too deep
        OSError: Permission, FileExists, etc

    Returns:
        ``False`` if some nodes were skipped, ``True`` ordinarily
    """
    if stack > 128:  # too deep
        if skip_deep:
            return False
        raise MaxRecursion(source)

    ret_code = True
    dest_root = Path(destin)
    dest_root.mkdir(parents=True, exist_ok=True)
    src_root = Path(source)
    if not src_root.is_dir():
        # Source directory does not exist
        raise TemplateMissingError(src_root)

    # Add missed files
    if stack == 0:
        dest_root.joinpath("LICENSE").write_text(
            edit_modify(config.license.read_text(), config))
        for missing_dirs in ("docs/_build", "docs/_static", "docs/_templates",
                             "docs/docs"):
            dest_root.joinpath(missing_dirs).mkdir(parents=True, exist_ok=True)
        dest_root.joinpath("docs/docs/coverage.svg").symlink_to(
            "../coverage.svg")

    for node in src_root.glob("*"):
        if node.is_file():
            # file
            if node.name[-4:] == ".pyc":
                continue
            dest_root.joinpath(node.name.replace("dot.", ".")).write_text(
                edit_modify(node.read_text(), config))
        elif node.is_symlink():
            # relative link
            # NEXT: in python3.9 os.readlink is replaced by Path().readlink
            symlink_target = Path(os.readlink(node)).relative_to(src_root)
            dest_root.joinpath(node.name.replace("dot.", ".")).symlink_to(
                dest_root.joinpath(symlink_target),
                target_is_directory=Path(os.readlink(node)).is_dir())
        elif node.name in (".git", ".venv", "__pycache__", "licenses"):
            # skip
            continue
        elif node.is_dir():
            # directory: recurse
            if node.name == "src":
                dirname = dest_root.joinpath(config.project.name)
            else:
                dirname = dest_root.joinpath(node.name.replace("dot.", "."))
            ret_code &= tree_copy(config,
                                  node,
                                  dirname,
                                  skip_deep=skip_deep,
                                  stack=stack + 1)
    return ret_code
