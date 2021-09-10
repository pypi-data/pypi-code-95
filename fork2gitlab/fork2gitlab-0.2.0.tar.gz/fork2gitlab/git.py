"""
fork2gitlab
Copyright (C) 2020 LoveIsGrief

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
from configparser import ConfigParser

from fork2gitlab.utils import run


def set_remote(repo_path, remote_url, remote="origin"):
    """
    Updates the remote of a given git repo

    @type repo_path: pathlib.Path
    @type remote_url: basestring
    @type remote: basestring
    """

    config = ConfigParser()
    config_path = str(repo_path / ".git" / "config")
    config.read([config_path])

    # Change the remote
    config.set(
        f'remote "{remote}"',
        "url",
        remote_url
    )
    # Write config
    with open(config_path, "w") as config_file:
        config.write(config_file)


def clone(url, path):
    path.parent.mkdir(exist_ok=True, parents=True)
    return run(
        "git",
        "clone",
        url,
        path,
    )


def clean(repo_path):
    return run(
        "git",
        "-C", repo_path,
        "clean",
        "-dfq"
    )


def merge(repo_path, url, branch):
    return run(
        "git",
        "-C", repo_path,
        "pull",
        url,
        branch
    )


def pull(repo):
    return run(
        "git",
        "-C", repo.path,
        "pull"
    )


def checkout(path, branch):
    return run(
        "git",
        "-C", path,
        "checkout",
        branch
    )


def push(path):
    return run(
        "git",
        "-c", "receive.denyCurrentBranch=ignore",
        "-C", path,
        "push"
    )
