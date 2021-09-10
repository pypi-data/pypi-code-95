#!/usr/bin/env python3
import json
import os
from setuptools import setup, find_packages

about = {}  # type: ignore
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'pyarmet', 'version.json')) as f:
    about = json.load(f)

# load the README file and use it as the long_description for PyPI
with open('README.md', 'r') as f:
    readme = f.read()

# package configuration - for reference see:
# https://setuptools.readthedocs.io/en/latest/setuptools.html#id9
setup(
    name="pyarmet",
    description=about['description'],
    long_description=readme,
    long_description_content_type='text/markdown',
    version=about['version'],
    author=about['author'],
    author_email=about['author_email'],
    url=about['url'],
    packages=find_packages(exclude=["*.tests"]),
    include_package_data=True,
    python_requires=">=3.6.*",
    install_requires=['absl-py',
                      'scikit-learn~=0.24.2',
                      'numpy==1.19.5',
                      'requests',
                      'mlflow',
                      'pandas',
                      'pandera',
                      'pandas_profiling',
                      'scipy~=1.5.4',
                      'boto3',
                      'keras==2.4.3',
                      'tensorflow>=2.5.0,<2.6.0'],
    license=about['license'],
    zip_safe=False,
    entry_points={
        'console_scripts': ['armet=armet.entry_points:main'],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.7',
    ],
    keywords=['python', 'armet', 'sklearn', 'federated learning']
)
