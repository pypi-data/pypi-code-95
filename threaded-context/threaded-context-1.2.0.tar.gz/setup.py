# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['threaded_context']
setup_kwargs = {
    'name': 'threaded-context',
    'version': '1.2.0',
    'description': 'Basic context manager with inheritance management.',
    'long_description': None,
    'author': 'François Schmidts',
    'author_email': 'francois@schmidts.fr',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
