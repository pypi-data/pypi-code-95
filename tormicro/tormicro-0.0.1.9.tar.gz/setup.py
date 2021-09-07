#!/usr/bin/env python
# -*- coding:utf-8 -*-

from setuptools import setup, find_packages

classifiers = """\
Development Status :: 4 - Beta
Intended Audience :: Developers
License :: OSI Approved :: Apache Software License
Programming Language :: Python :: 3
Topic :: Database
Topic :: Software Development :: Libraries :: Python Modules
Operating System :: Unix
Operating System :: MacOS :: MacOS X
Operating System :: Microsoft :: Windows
Operating System :: POSIX
"""

setup(
    name='tormicro',
    # auto generate version
    use_scm_version=True,
    author='He Bai',
    author_email='bailaohe@gmail.com',

    description='A tornado-based microservice booster',

    keywords=["tornado", "microservice", "web", "restful"],
    url='https://github.com/bailaohe/parade',
    platforms=["any"],
    classifiers=filter(None, classifiers.split("\n")),

    install_requires=[
        'aiofiles==0.4.0', 'aiohttp==3.6.2', 'aiotask-context==0.6.1', 'argparse==1.4.0',
        'asyncio==3.4.3', 'asynctest==0.13.0', 'coverage==5.0.3', 'flake8==3.7.9',
        'jsonschema==3.2.0', 'logfmt==0.4', 'mypy==0.761', 'PyYAML==5.4', 'requests==2.22.0',
        'tornado==6.0.3', 'mergedeep==1.3.4', 'aliyun-log-python-sdk==0.6.56',
        'tornado-swagger==1.2.10'
    ],

    packages=find_packages('.'),
    package_dir=({'': '.'}),
    zip_safe=False,

    include_package_data=True,
    package_data={'': ['*.json', '*.xml', '*.yml', '*.yaml', '*.tpl']},

    entry_points={
        'console_scripts': [
            'tormicro = tormicro.server:main',
        ],
    },

    setup_requires=[
        "setuptools_scm>=1.5",
    ],
    # python_requires=">=3.6",
    # download_url='https://github.com/bailaohe/parade/tarball/0.1',
)
