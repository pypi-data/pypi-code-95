#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import find_packages, setup
import os

REQUIRES = [
    'pandas',
    'numpy',
    'tqdm',
    'scikit-learn'
]

setup(
    name='wllutils',
    version='0.0.7.1',
    description=('utils of wll' ),
    author='weiliulei',
    author_email='18500964455@163.com' ,
    maintainer='weiliulei',
    maintainer_email='18500964455@163.com' ,
    license = 'MIT',
    packages=find_packages(),
    platforms=['all',],
    # url='https://github.com/Wei-Liulei/utils',
    install_requires=REQUIRES,
    pbr=True
)

# pip install twine
# 打包 tar.gz ,whl,  windows 下 bdist_wininst
# python .\setup.py sdist bdist_wheel # bdist_wininst  windows
# python ./setup.py sdist bdist_wheel # bdist_wininst  linux
# twine upload dist/*


# 免密上传
# 用户目录下 .pypirc 文件 
# [distutils]
# index-servers =
#   pypi
# 
# [pypi]
# repository = https://upload.pypi.org/legacy/
# username: ********
# password: ********

