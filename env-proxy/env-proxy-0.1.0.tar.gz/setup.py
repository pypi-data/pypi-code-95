# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['env_proxy']
setup_kwargs = {
    'name': 'env-proxy',
    'version': '0.1.0',
    'description': 'Creates a class used to query environmental variables with typehinting a conversion to basic Python types.',
    'long_description': None,
    'author': 'Tomas Votava',
    'author_email': 'info@tomasvotava.eu',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
