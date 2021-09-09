# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['qikdb']

package_data = \
{'': ['*']}

install_requires = \
['termcolor>=1.1.0,<2.0.0']

setup_kwargs = {
    'name': 'qikdb',
    'version': '0.3.1',
    'description': 'Simple, and easy to use Python Database using JSON.',
    'long_description': None,
    'author': 'Andrew Bordis',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
