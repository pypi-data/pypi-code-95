# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['time_log']
install_requires = \
['pretty-tables>=1.3.0,<2.0.0', 'yacf>=1.1.0,<2.0.0']

setup_kwargs = {
    'name': 'time-log',
    'version': '0.1.0',
    'description': 'Prototype for a time tracker/logger command line utility',
    'long_description': None,
    'author': 'Max Resing',
    'author_email': 'max.resing@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
