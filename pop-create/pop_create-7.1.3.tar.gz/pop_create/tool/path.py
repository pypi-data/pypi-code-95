import os
import pathlib
import shutil
from typing import Callable


def __init__(hub):
    hub.tool.path.IGNORE = []


def touch(hub, path: pathlib.Path):
    """
    Make sure that a file exists, it's ok if the file already exists
    """
    hub.tool.path.mkdir(path.parent)
    if not path.exists():
        path.touch()


def mkdir(hub, path: pathlib.Path):
    """
    make sure that a directory and it's parents exist
    """
    for p in path.parents:
        # Make sure parent's exist before continuing
        hub.tool.path.mkdir(p)
    if not path.exists():
        path.mkdir()


def copy(hub, src, dst, *, follow_symlinks: bool = True):
    """
    Copy function that skips existing files
    """
    if os.path.isdir(dst):
        dst = os.path.join(dst, os.path.basename(src))
    if str(dst) in hub.tool.path.IGNORE:
        hub.log.debug(f"Ignoring target: {dst}")
        return dst
    elif os.path.isdir(dst) or os.path.isdir(src):
        return dst
    elif os.path.exists(dst):
        hub.log.debug(f"Skipping target that already exists: {dst}")
        return dst
    hub.log.debug(f"Writing new file: {dst}")
    shutil.copyfile(src, dst, follow_symlinks=follow_symlinks)
    shutil.copystat(src, dst, follow_symlinks=follow_symlinks)
    return dst


def copy2(hub, src, dst, *, follow_symlinks: bool = True):
    if str(dst) in hub.tool.path.IGNORE:
        hub.log.debug(f"Ignoring overwrite target: {dst}")
        return dst
    return shutil.copy2(src, dst, follow_symlinks=follow_symlinks)


def copytree(hub, src: pathlib.Path, dst: pathlib.Path, copy_function: Callable):
    if src.is_dir():
        if not dst.exists():
            dst.mkdir()
        for src_subdir in src.iterdir():
            hub.tool.path.copytree(src_subdir, dst / src_subdir.name, copy_function)
    else:
        copy_function(src, dst)


def rmtree(hub, src: pathlib.Path):
    """
    Remove a directory and all files underneath it
    """
    shutil.rmtree(src, ignore_errors=True)
    if src.exists():
        src.rmdir()


def delete(hub, src: pathlib.Path):
    if src.exists():
        src.unlink()
