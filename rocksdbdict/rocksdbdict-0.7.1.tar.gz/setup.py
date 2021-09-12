# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['rocksdbdict']
install_requires = \
['python-rocksdb>=0.7.0,<0.8.0']

setup_kwargs = {
    'name': 'rocksdbdict',
    'version': '0.7.1',
    'description': '',
    'long_description': None,
    'author': 'Adam Marples',
    'author_email': 'adammarples@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
