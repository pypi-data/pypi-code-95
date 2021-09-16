#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
__version__ = '1.1.18'

with open('README.md', encoding='utf-8') as f:
    readme = f.read()

requirements = [
    "requests",
    "tqdm",
    "ipykernel",
    "traitlets",
    "jupyter_core",
    "importlib-metadata",
    "numpy",
    "packaging>=21.0",
    "click",
    "more_itertools",
    "google-resumable-media",
    "toml",
    "GitPython"]

setup(
    name="pyhectiqlab",
    version=__version__,
    description='Python client to use the hectiq lab',
    long_description=readme,
    long_description_content_type='text/markdown',
    author='Edward Laurence',
    author_email='edwardl@hectiq.ai',
    url='https://www.hectiq.ai',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    zip_safe=False,
    keywords='pip requirements imports',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Scientific/Engineering',
        'Intended Audience :: Science/Research',
    ],
    test_suite='tests',
    entry_points={
        'console_scripts': [
            'hectiqlab=pyhectiqlab.cli:main',
        ],
    },
)