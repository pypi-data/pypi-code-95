# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fastio_cli']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'fastio-cli',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'fastio.dev',
    'author_email': 'opensource@fastio.dev',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
