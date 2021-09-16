"""
This file is part of the Omedia Skyworker Processor.

(c) 2021 Omedia <welcome@omedia.dev>

For the full copyright and license information, please view the LICENSE
file that was distributed with this source code.

Written by Temuri Takalandze <t.takalandze@omedia.dev>, August 2021
"""

import os
import re

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


def get_requirements(filename: str) -> list[str]:
    """
    Get requirements file content by filename.

    :param filename: Name of requirements file.
    :return: Content of requirements file.
    """

    return open("requirements/" + filename).read().splitlines()


def get_package_version() -> str:
    """
    Read the version of Skyworker Processor module without importing it.

    :return: The version.
    """

    version = re.compile(r"__version__\s*=\s*\"(.*?)\"")
    base = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(base, "skyworker_processor/__init__.py")) as file:
        for line in file:
            match = version.match(line.strip())
            if not match:
                continue
            return match.groups()[0]


setup(
    name="skyworker_dev_electricity_price_random_other",
    version=get_package_version(),
    author="Temuri Takalandze",
    author_email="welcome@omedia.dev",
    description="Skyworker AI Processor",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="http://example.com",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(exclude=["tests", "tests.*"]),
    python_requires=">=3.6",
    install_requires=get_requirements("default.txt"),
    test_suite="tests",
    tests_require=get_requirements("test.txt"),
)
