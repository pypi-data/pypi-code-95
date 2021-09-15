# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['jsonpatch_to_mongodb']
setup_kwargs = {
    'name': 'jsonpatch-to-mongodb',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Derfirm',
    'author_email': 'beulea@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
