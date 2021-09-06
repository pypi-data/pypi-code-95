# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = {"": "src"}

packages = ["extended"]

package_data = {"": ["*"]}

setup_kwargs = {
    "name": "extended",
    "version": "0.1",
    "description": "Some description.",
    "long_description": "Module 1\n========\n",
    "author": "Sébastien Eustace",
    "author_email": "sebastien@eustace.io",
    "maintainer": "None",
    "maintainer_email": "None",
    "url": "https://python-poetry.org/",
    "package_dir": package_dir,
    "packages": packages,
    "package_data": package_data,
}
from build import *

build(setup_kwargs)

setup(**setup_kwargs)
