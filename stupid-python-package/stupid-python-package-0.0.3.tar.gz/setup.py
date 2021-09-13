# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['stupid_python_package']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'stupid-python-package',
    'version': '0.0.3',
    'description': 'The Stupidist python package for testing poerty build and publish',
    'long_description': None,
    'author': 'Süleyman ERGEN',
    'author_email': 'suleymanergen32@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
