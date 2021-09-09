# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cov19py']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.7.4,<4.0.0', 'xmltodict>=0.12.0,<0.13.0']

setup_kwargs = {
    'name': 'cov19py',
    'version': '0.1.3',
    'description': '',
    'long_description': None,
    'author': 'SpaceDEV',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/SpaceDEVofficial/corona.py',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
