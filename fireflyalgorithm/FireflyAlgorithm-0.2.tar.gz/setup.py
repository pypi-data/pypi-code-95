# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['FireflyAlgorithm']
install_requires = \
['numpy>=1.21.2,<2.0.0']

setup_kwargs = {
    'name': 'fireflyalgorithm',
    'version': '0.2',
    'description': 'Firefly algorithm implementation.',
    'long_description': None,
    'author': 'firefly-cpp',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<3.11',
}


setup(**setup_kwargs)
