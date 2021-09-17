# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['borderline']
setup_kwargs = {
    'name': 'borderline',
    'version': '0.1.1',
    'description': 'Tests that new imports within a module respect the public API boundary.',
    'long_description': None,
    'author': 'Christoph Klein',
    'author_email': 'ckleinemail@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ctk3b/borderline',
    'py_modules': modules,
    'python_requires': '>=3.6.2,<4.0',
}


setup(**setup_kwargs)
