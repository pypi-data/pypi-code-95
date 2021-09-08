# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['coloredconsole']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'coloredconsole',
    'version': '0.0.1',
    'description': '',
    'long_description': None,
    'author': 'Andrew Bordis',
    'author_email': 'andrewbordis@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
