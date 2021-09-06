# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['simple_status_client']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.26.0,<3.0.0', 'yarl>=1.6.3,<2.0.0']

setup_kwargs = {
    'name': 'simple-status-client',
    'version': '0.1.0',
    'description': 'A package for interacting with the Simple Status Server',
    'long_description': None,
    'author': 'Benjamin Smith',
    'author_email': 'bravosierra99@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
