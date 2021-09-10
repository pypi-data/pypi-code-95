#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re

from setuptools import setup


def get_version(*file_paths):
    """Retrieves the version from pipfreezer/__init__.py"""
    filename = os.path.join(os.path.dirname(__file__), *file_paths)
    version_file = open(filename).read()
    version_match = re.search(
        r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M
    )  # noqa
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


version = get_version("pipfreezer", "__init__.py")

readme = open("README.md").read()
history = open("HISTORY.md").read()
requirements = open("requirements.txt").readlines()

setup(
    name="pip-freezer",
    version=version,
    description="""For the organized, but lazy developer, meaning that you'll update a package, but you don't want to be bothered with updating the requirements file. Pip Freezer pins packages no matter which requirements file they live in and maintains your comments and line breaks.""",
    long_description=readme + "\n\n" + history,
    long_description_content_type="text/markdown",
    author="Tim Santor",
    author_email="tsantor@xstudios.com",
    url="https://bitbucket.org/tsantor/pip-freezer",
    packages=[
        "pipfreezer",
    ],
    include_package_data=True,
    package_data={"sample": ["data/pipfreezer.cfg"]},
    install_requires=requirements,
    license="MIT",
    zip_safe=False,
    keywords="pip-freezer",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    entry_points={"console_scripts": ["pipfreezer = pipfreezer.pipfreezer:run"]},
)
