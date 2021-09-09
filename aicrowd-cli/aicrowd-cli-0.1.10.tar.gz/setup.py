#!/usr/bin/env python
"""
Build and install the CLI
"""

from pathlib import Path

from setuptools import setup, find_packages

import versioneer

README = Path("README.md").read_text()
REPO_URL = "https://gitlab.aicrowd.com/aicrowd/aicrowd-cli"

current_dir = Path(__file__).resolve().parent
version = versioneer.get_version()

with open(str(current_dir / "requirements" / "build.txt")) as reqs_file:
    reqs = reqs_file.read().split()

setup(
    name="aicrowd-cli",
    description="A CLI app to interact with AIcrowd",
    long_description=README,
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    version=version,
    cmdclass=versioneer.get_cmdclass(),
    install_requires=reqs,
    entry_points={
        "console_scripts": [
            "aicrowd=aicrowd.cli:cli",
        ]
    },
    python_requires=">=3.6",
    license="MIT",
    author="Yoogottam Khandelwal",
    author_email="yoogottamk@outlook.com",
    url=REPO_URL,
    download_url=f"{REPO_URL}/-/archive/{version}/aicrowd-cli-{version}.tar.gz",
    keywords=["AIcrowd", "CLI"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Environment :: Console",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    include_package_data=True,
)
