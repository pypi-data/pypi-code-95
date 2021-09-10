#!/usr/bin/env python
# -*- coding:utf-8 -*-
from setuptools import setup, find_packages

# with open('README.md', encoding='utf-8') as f:
#     long_description = f.read()

setup(
    name="utx",
    version="0.0.3",
    keywords=["utx", "airtest", "pytest", "ui", "tools"],
    description='UTX will help you write application automated tests more easily!',
    long_description='UTX will help you write application automated tests more easily!',
    long_description_content_type='text/markdown',
    license="Apache License",

    # url="https://github.com/Pactortester/utx",
    author="lijiawei",
    author_email="1456470136@qq.com",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console :: Curses",
        "Operating System :: MacOS",
        "Operating System :: POSIX",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: CPython"
    ],
    entry_points="""
    [console_scripts]
    utx = utx.cli.cli:main
    """,
    packages=find_packages(),
    include_package_data=True,
    platforms="any",
    install_requires=["tep~=0.8.9", "airtest~=1.2.2", "tenacity~=8.0.1", "allure-pytest~=2.9.43", "pocoui~=1.0.83",
                      "tidevice~=0.4.18", "faker~=4.18.0", "jmespath~=0.10.0", "loguru~=0.5.3", "pytest-xdist~=2.3.0",
                      "PyYAML~=5.4.1", "allure-python-commons~=2.9.43"]
)
