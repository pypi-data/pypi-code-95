# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['aiofilters']
setup_kwargs = {
    'name': 'aiofilters',
    'version': '1.0.0',
    'description': 'You must install Aiogram to use this library! You can see how to use it in GitHub Repository https://github.com/Bananchik204/AioFilters',
    'long_description': None,
    'author': 'Furret',
    'author_email': 'durovam0@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
