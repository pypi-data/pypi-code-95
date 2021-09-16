# Copyright 2021 Mathew Odden

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf8") as fh:
    long_desc = fh.read()

setup(
    name="spdy-py",
    version="0.1.0",
    author="Mathew Odden",
    author_email="mrodden@us.ibm.com",
    url="https://github.com/mrodden/spdy-py",
    description="A pure Python implementation of the SDPY/3.x protocol",
    long_description=long_desc,
    long_description_content_type="text/markdown",
    license="LGPL",
    packages=find_packages("src"),
    package_dir={"": "src"},
    package_data={"spdy": ["py.typed", "*.pyi"]},
    include_package_data=True,
    zip_safe=False,
    install_requires=[],
    entry_points={},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: "
        "GNU Library or Lesser General Public License (LGPL)",
    ],
    python_requires=">=3.6",
)
