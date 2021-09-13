# Copyright 2020 Karlsruhe Institute of Technology
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import glob
import json
import os
import re
import shutil
import sys

import click
from flask import current_app

from kadi.cli.main import kadi
from kadi.cli.utils import check_env
from kadi.cli.utils import danger
from kadi.cli.utils import run_command
from kadi.cli.utils import success
from kadi.lib.storage.local import LocalStorage


# The following code is a slightly modified version of flask-static-digest, which is
# available at the following URL: https://github.com/nickjj/flask-static-digest
#
# flask-static-digest is licensed under the MIT license:
#
# The MIT License (MIT)
#
# Copyright (c) 2019 Nick Janetakis
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# 'Software'), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


DIGESTED_FILE_REGEX = r"-[a-f\d]{32}"


@kadi.group()
def assets():
    """Utility commands for asset management."""


def _run_npm(args, prefix):
    if not shutil.which("npm"):
        danger("'npm' not found in PATH, maybe Node.js is not installed?")
        sys.exit(1)

    if prefix is not None:
        prefix = ["--prefix", prefix]
    else:
        prefix = []

    run_command(["npm"] + args + prefix)


def _is_compiled_file(filepath):
    return (
        re.search(DIGESTED_FILE_REGEX, os.path.basename(filepath))
        or filepath == current_app.config["MANIFEST_PATH"]
    )


def _compile_assets():
    static_path = current_app.static_folder
    search_path = os.path.join(static_path, "**", "*")
    storage = LocalStorage()

    # Collect all static files to "compile".
    files = []
    for item in glob.iglob(search_path, recursive=True):
        if os.path.isfile(item) and not _is_compiled_file(item):
            files.append(item)

    manifest = {}
    # Generate the manifest.
    for file in files:
        rel_filepath = os.path.relpath(file, static_path).replace("\\", "/")
        filename, file_extension = os.path.splitext(rel_filepath)
        digest = storage.get_checksum(file)

        digested_filepath = f"{filename}-{digest}{file_extension}"
        manifest[rel_filepath] = digested_filepath

        # Copy the file while preserving permissions and metadata if supported.
        full_digested_filepath = os.path.join(static_path, digested_filepath)
        shutil.copy2(file, full_digested_filepath)

    # Finally, save the manifest file.
    with open(current_app.config["MANIFEST_PATH"], mode="w", encoding="utf-8") as f:
        f.write(json.dumps(manifest, ensure_ascii=False))


def _clean_assets():
    search_path = os.path.join(current_app.static_folder, "**", "*")

    for item in glob.iglob(search_path, recursive=True):
        if os.path.isfile(item) and _is_compiled_file(item):
            os.remove(item)

    try:
        # The manifest file might already get deleted in the previous step.
        os.remove(current_app.config["MANIFEST_PATH"])
    except FileNotFoundError:
        pass


prefix_option = click.option(
    "-p",
    "--prefix",
    type=click.Path(exists=True),
    help="The project root path that contains all configuration files needed by npm.",
)


@assets.command()
@prefix_option
@check_env
def build(prefix):
    """Build and compile all static assets for use in production.

    This will install all missing frontend dependencies, run webpack to build all
    minified asset bundles and then tag all static files using their MD5 hash.
    Additionally, a manifest file "manifest.json" mapping the original files to their
    tagged counterparts will also be created.
    """
    _clean_assets()

    _run_npm(["install", "--silent", "--no-audit", "--no-fund"], prefix=prefix)
    _run_npm(["run", "build"], prefix=prefix)

    _compile_assets()

    success("Assets built successfully.")


@assets.command()
@prefix_option
@check_env
def dev(prefix):
    """Build all static assets for use in development.

    This will install all missing frontend dependencies and then run webpack to build
    all asset bundles.
    """
    _clean_assets()

    _run_npm(["install", "--silent", "--no-audit", "--no-fund"], prefix=prefix)
    _run_npm(["run", "dev"], prefix=prefix)

    success("Assets built successfully.")


@assets.command()
@prefix_option
@check_env
def watch(prefix):
    """Build and watch all static assets for use in development.

    This will install all missing frontend dependencies and then run webpack to build
    and watch all asset bundles.
    """
    _clean_assets()

    _run_npm(["install", "--silent", "--no-audit", "--no-fund"], prefix=prefix)
    _run_npm(["run", "watch"], prefix=prefix)
