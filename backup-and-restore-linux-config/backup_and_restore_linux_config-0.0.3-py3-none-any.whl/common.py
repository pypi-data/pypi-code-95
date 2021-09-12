import os
import shutil
import logging
logging.basicConfig(format='[%(funcName)s] %(message)s', level=logging.DEBUG)

from typing import Tuple, List
from pathlib import Path


import difflib
from datetime import datetime
from colorama import Fore, Style
import click
from datetime import datetime

EXCLUDE_FOLDER = [".git", ".mypy_cache"]
EXCLUDE_FILE = ["TODO.md", ".swp"]


def skip_this_user(file: Path, backup: Path, selected_users: List[str]) -> bool:

    user = get_user(file, root_path=backup)

    if user not in selected_users:
        print(f"user {user} skipped 1")
        return True

    if file_exists_in_other_higher_priority_user(file, backup, selected_users):
        print(f"user {user} skipped 2")
        return True

    return False


def get_user(file: Path, root_path: Path = Path("/")) -> str:

    rel = file.relative_to(root_path)

    parts = list(rel.parts)

    assert parts[0] == "home"

    return parts[1]


# TODO: handle not user paths
#    if len(rel.parts)>2 and rel.parts[1] != "home":
#        return path


def change_user_path(path: Path, new_user: str, root_path: Path = Path("/")) -> Path:
    """ Change user name of the path. The given path shoud be absolute and
    therefore the user name is in the second position (after 'home' folder)

    >>> change_user_path(Path('/home/foo/.local/bin/myprogram.sh'), 'bar')
    Path('/home/bar/.local/bin/myprogram.sh')
    """
    #    if not path.is_absolute():
    #        raise ValueError("Path is not absolute")

    rel = path.relative_to(root_path)

    parts = list(rel.parts)
    # import pdb; pdb.set_trace()
    parts[1] = new_user
    path = root_path / Path(*parts)

    return path


def _file_mtime(path):
    t = datetime.fromtimestamp(os.stat(path).st_mtime)
    return t.strftime("%Y-%m-%d %M:%M:%S")


def print_diff(fromfile: Path, tofile: Path):
    with open(fromfile) as ff:
        fromlines = ff.readlines()
    with open(tofile) as tf:
        tolines = tf.readlines()
    fromdate = _file_mtime(fromfile)
    todate = _file_mtime(tofile)
    diff = difflib.unified_diff(
        fromlines, tolines, str(fromfile), str(tofile), fromdate, todate, n=3
    )
    has_diff = False
    for i in diff:
        has_diff = True
        if i.startswith("---"):
            i = Fore.RED + Style.BRIGHT + i + Style.RESET_ALL
        elif i.startswith("+++"):
            i = Fore.GREEN + Style.BRIGHT + i + Style.RESET_ALL
        elif i.startswith("-"):
            i = Fore.RED + i + Fore.RESET
        elif i.startswith("+"):
            i = Fore.GREEN + i + Fore.RESET
        elif i.startswith("@"):
            i = Fore.BLUE + i + Fore.RESET
        print("\t" + i, end="")
    return has_diff


def file_exists_in_other_higher_priority_user(
    file: Path, backup: Path, users_list: List[str]
) -> bool:
    #    user = get_user_path(file, backup)

    index_actual_user = users_list.index(get_user(file, root_path=backup))

    higher_level_users = users_list[0 :index_actual_user]
    for user in higher_level_users:
        new_path = change_user_path(file, user, backup)
        if new_path.is_file():
            return True

    return False


def is_first_directory_bigger_than_second(first, second) -> bool:
    return os.listdir(first) > os.listdir(second)
