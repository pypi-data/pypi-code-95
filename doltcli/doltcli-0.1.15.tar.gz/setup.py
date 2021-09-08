# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['doltcli']

package_data = \
{'': ['*']}

extras_require = \
{':python_version < "3.7"': ['dataclasses>=0.6']}

setup_kwargs = {
    'name': 'doltcli',
    'version': '0.1.15',
    'description': "Slim Python interface for Dolt's CLI API.",
    'long_description': None,
    'author': 'Max Hoffman',
    'author_email': 'max@dolthub.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'extras_require': extras_require,
    'python_requires': '>=3.6.1,<4.0',
}


setup(**setup_kwargs)
