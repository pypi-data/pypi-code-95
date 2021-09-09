# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['cooper_util']
install_requires = \
['loguru>=0.5.3,<0.6.0', 'rich>=10.9.0,<11.0.0']

setup_kwargs = {
    'name': 'cooper-util',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Bao Hengtao',
    'author_email': 'baohengtao@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
