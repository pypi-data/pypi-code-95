#!/usr/bin/env python
# -*- coding:utf-8 -*-
from setuptools import setup, find_packages

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="monitors",
    version="1.0.3",
    keywords=["grafana", "monitors", "process monitor", "system monitor", "influxdb"],
    description="monitor tools",
    long_description=long_description,
    long_description_content_type='text/markdown',
    license="MIT Licence",

    url="https://github.com/Pactortester/monitors",
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
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: System :: Networking :: Monitoring",
        "Topic :: Software Development :: Testing",
        "Typing :: Typed",
    ],

    packages=find_packages(),
    include_package_data=True,
    platforms="any",
    install_requires=["psutil~=5.8.0", "influxdb~=5.3.1", "requests~=2.26.0"]
)
