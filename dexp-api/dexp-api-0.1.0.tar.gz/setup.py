# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dexp_api']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp[speedups]>=3.7.4,<4.0.0',
 'coloredlogs>=15.0.1,<16.0.0',
 'priority>=2.0.0,<3.0.0']

setup_kwargs = {
    'name': 'dexp-api',
    'version': '0.1.0',
    'description': 'In planning flexible and powerful discord api wrapper for python.',
    'long_description': None,
    'author': 'Bast',
    'author_email': 'bast@fastmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
