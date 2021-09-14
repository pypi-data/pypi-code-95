#!/usr/bin/env python3
"""Pypi configuration."""

import os

import setuptools  # type: ignore


def _read_reqs(relpath):
    fullpath = os.path.join(os.path.dirname(__file__), relpath)
    with open(fullpath, encoding="utf-8") as open_file:
        return [s.strip() for s in open_file.readlines() if (s.strip() and not s.startswith("#"))]


with open("README.md", encoding="utf-8") as readme_file:
    readme = readme_file.read()

setuptools.setup(
    name="FutureLog",
    version="0.1.1",
    description="Consume logs by block in async application",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Kevin Petremann",
    author_email="kpetrem@gmail.com",
    packages=["futurelog"],
    include_package_data=True,
    python_requires=">=3.6",
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: System :: Logging",
    ],
    tests_require=_read_reqs("requirements/tests.txt"),
    url="https://github.com/kpetremann/futurelog",
    project_urls={
        "Source": "https://github.com/kpetremann/futurelog",
    },
)
