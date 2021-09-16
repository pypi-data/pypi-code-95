# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['telecoin']

package_data = \
{'': ['*']}

install_requires = \
['Pyrogram==1.2.9', 'aiohttp==3.7.4.post0']

setup_kwargs = {
    'name': 'telecoin',
    'version': '0.0.6',
    'description': 'Simple library to make payments via telegram bitcoin exchangers',
    'long_description': '**Slava Fisting Anal**',
    'author': 'Marple',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/marple-git/telecoin',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
