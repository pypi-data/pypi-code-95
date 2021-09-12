# -*- coding:utf-8  -*-

from setuptools import *

setup(
    name = 'Python-Extension',
    version = '1.4.1',
    description = 'Python extension functions',
    license = 'GPL',
    author = 'Yile Wang',
    author_email = '36210280@qq.com',
    packages = find_packages(),
    python_requires = '>=2.7',
    package_requires = ['python-docx>=0.8'],
    include_package_data = True
    )
