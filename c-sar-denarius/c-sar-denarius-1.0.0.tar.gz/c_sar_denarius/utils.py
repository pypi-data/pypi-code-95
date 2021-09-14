#
# Copyright (c) 2021 Genome Research Ltd
#
# Author: CASM/Cancer IT <cgphelp@sanger.ac.uk>
#
# This file is part of c-sar-denarius.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# 1. The usage of a range of years within a copyright statement contained within
# this distribution should be interpreted as being equivalent to a list of years
# including the first and last year specified and all consecutive years between
# them. For example, a copyright statement that reads ‘Copyright (c) 2005, 2007-
# 2009, 2011-2012’ should be interpreted as being identical to a statement that
# reads ‘Copyright (c) 2005, 2007, 2008, 2009, 2011, 2012’ and a copyright
# statement that reads ‘Copyright (c) 2005-2012’ should be interpreted as being
# identical to a statement that reads ‘Copyright (c) 2005, 2006, 2007, 2008,
# 2009, 2010, 2011, 2012’.
import hashlib
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import List

from packaging.version import InvalidVersion
from packaging.version import Version
from pkg_resources import require
from pkg_resources import resource_listdir

MY_VERSION = require(__name__.split(".")[0])[0].version


def version():
    return MY_VERSION


def sha256(fname):
    hash_sha256 = hashlib.sha256()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()


def files_not_seen(input: str, file_seen: List[str]):
    all_files = []
    for root, dirs, files in os.walk(input):
        for f in files:
            all_files.append(os.path.join(root, f))

    missed_files = sorted(list(set(all_files).difference(set(file_seen))))
    logging.info(f"{len(all_files)} files found in input area,")
    logging.info(f"{len(file_seen)} files were captured by this configuration.")
    miss_count = len(missed_files)
    if miss_count > 0:
        logging.warning(f"{miss_count} files that were not captured, run with '--loglevel debug' for listing")
        if logging.getLogger().getEffectiveLevel() == logging.DEBUG:
            for f in missed_files:
                logging.debug()


def template_versions():
    v_list = []
    for f in resource_listdir(__name__, "resources/structure"):
        (name, ext) = os.path.splitext(f)
        if ext == ".yaml":
            v_list.append(Version(name))  # only expect valid PEP440
    return v_list


def c_sar_version(root: str):
    """
    Get and parse c-sar version file from expected location
    """
    v_list = template_versions()

    ver_file = Path(os.path.join(root, "c-sar.version"))
    version = None
    config_ver = None
    if ver_file.is_file():
        with open(ver_file, "r") as vfh:
            version = vfh.readline().strip()
        try:
            Version(version)
        except InvalidVersion:
            raise ValueError(f"Version '{version}' does not conform to PEP440")
        if Version(version) in v_list:
            config_ver = version
    else:
        logging.warning(f"Unable to find 'c-sar.version' in result folder, using latest config")
        version = "?"
    if config_ver is None:
        config_ver = str(max(v_list))
    return (version, config_ver)


def process_log_and_exit(r: subprocess.CompletedProcess, message):
    logging.critical(message)
    logging.critical(f"COMMAND: {r.args}")
    logging.critical(f"STDOUT: {r.stdout}")
    logging.critical(f"STDERR: {r.stderr}")
    sys.exit(2)
