# -*- coding=utf-8 -*-

from setuptools import *

file = open('README.md', 'r', encoding='utf-8')
text = file.read()
file.close()

setup(
    name = 'Python-Extension',
    version = '1.3.4',
    description = 'Python extension functions',
    long_description = text,
    license = 'GPL',
    author = 'Yile Wang',
    author_email = '36210280@qq.com',
    packages = find_packages(),
    python_requires = '>=2.7',
    package_requires = ['python-docx>=0.8'],
    include_package_data = True
    )
