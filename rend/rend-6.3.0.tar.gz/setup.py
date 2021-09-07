#!/usr/bin/env python3
import os
import pathlib
import shutil

from setuptools import Command
from setuptools import setup

NAME = "rend"
DESC = "A collection of tools to render text files into data structures"

# Version info -- read without importing
_locals = {}
with open(f"{NAME}/version.py") as fp:
    exec(fp.read(), None, _locals)
VERSION = _locals["version"]
SETUP_DIRNAME = os.path.dirname(__file__)
if not SETUP_DIRNAME:
    SETUP_DIRNAME = os.getcwd()

with open("README.rst", encoding="utf-8") as f:
    LONG_DESC = f.read()

requires_found = None
req_file = os.path.join("requirements", "base.txt")
if os.path.exists(req_file):
    requires_found = req_file
else:
    # We are running from inside an sdist:
    egg_info_dir = os.path.join(os.path.dirname(__file__), f"{NAME}.egg-info")
    requires_txt = os.path.join(egg_info_dir, "requires.txt")
    if os.path.exists(requires_txt):
        requires_found = requires_txt


with open(requires_found) as f:
    REQUIREMENTS = f.read().splitlines()

REQUIREMENTS_EXTRA = {}
EXTRA_PATH = pathlib.Path("requirements", "extra")
if EXTRA_PATH.exists():
    REQUIREMENTS_EXTRA["full"] = set()
    for extra in EXTRA_PATH.iterdir():
        with extra.open("r") as f:
            REQUIREMENTS_EXTRA[extra.stem] = f.read().splitlines()
            REQUIREMENTS_EXTRA["full"].update(REQUIREMENTS_EXTRA[extra.stem])


class Clean(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        for subdir in (NAME, "tests"):
            for root, dirs, files in os.walk(
                os.path.join(os.path.dirname(__file__), subdir)
            ):
                for dir_ in dirs:
                    if dir_ == "__pycache__":
                        shutil.rmtree(os.path.join(root, dir_))


def discover_packages():
    modules = []
    # dot-delimited list of modules to not package. It's not good to package tests:
    skip_mods = ["tests"]
    for package in (NAME,):
        for root, _, files in os.walk(os.path.join(SETUP_DIRNAME, package)):
            pdir = os.path.relpath(root, SETUP_DIRNAME)
            modname = pdir.replace(os.sep, ".")
            if modname not in skip_mods:
                modules.append(modname)
    return modules


setup(
    name=NAME,
    author="Thomas S Hatch",
    author_email="thatch@vmware.com",
    url="https://gitlab.com/saltstack/pop/rend",
    version=VERSION,
    install_requires=REQUIREMENTS,
    extras_require=REQUIREMENTS_EXTRA,
    description=DESC,
    long_description=LONG_DESC,
    long_description_content_type="text/x-rst",
    classifiers=[
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Development Status :: 5 - Production/Stable",
    ],
    entry_points={
        "console_scripts": [
            "rend = rend.scripts:start",
        ],
    },
    packages=discover_packages(),
    cmdclass={"clean": Clean},
)
