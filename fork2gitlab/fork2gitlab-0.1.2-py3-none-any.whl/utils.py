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
import subprocess
from urllib.parse import urlparse, urlunparse

DOT_GIT = ".git"


def run(*args):
    return subprocess.run([str(arg) for arg in args]).check_returncode()


def remove_ext(string, ext):
    if string.endswith(ext):
        string = string[:-len(ext)]
    return string


def str2int(string):
    try:
        return int(string)
    except:
        return None


def get_authorized_url(url, user, password):
    """
    Creates a URL with a user and password

    @type url: basestring
    @type user:
    @type password: basestring
    @rtype: basestring
    """
    parsed = urlparse(url)
    if not parsed.username:
        parsed = parsed._replace(netloc=f"{user}:{password}@{parsed.netloc}")

    return urlunparse(parsed)
