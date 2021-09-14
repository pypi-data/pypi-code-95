#!/usr/bin/env python
# -*- coding: utf-8 -*-


from glob import glob
from os.path import basename
#from os.path import dirname
#from os.path import join
from os.path import splitext
from setuptools import find_packages, setup

NAME = "arnica"
VERSION = "1.11.0"

setup(
    name=NAME,
    version=VERSION,
    description='Open Source library CFD toolkit',
    author='CoopTeam-CERFACS',
    author_email='coop@cerfacs.com',
    url='',
    keywords=["ARNICA"],
    packages=find_packages("src"),
    package_dir={"": "src"},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    license="CeCILL-B FREE SOFTWARE LICENSE AGREEMENT",
    install_requires=[
        'numpy',
        'scipy',
        'matplotlib',
        'h5py',
        'PyYAML>=3.13',
        'lxml',
        'hdfdict',
        'satis',
        'click',
        'pandas',
        'plotille',
        'kokiy',
        ],
    tests_require = [
        'pytest',
        'pytest-cov',
        'pytest-allclose',
    ],
    entry_points={
        "console_scripts": [
            "arnica = arnica.cli:main_cli",
        ]
    },
)
