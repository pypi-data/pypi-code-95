# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['foragerpy']

package_data = \
{'': ['*']}

install_requires = \
['Pillow>=8.3.1,<9.0.0', 'aiohttp>=3.7.4,<4.0.0', 'tqdm>=4.61.2,<5.0.0']

setup_kwargs = {
    'name': 'foragerpy',
    'version': '0.0.1',
    'description': 'The official Python client for Forager.',
    'long_description': None,
    'author': 'Fait Poms',
    'author_email': 'faitpoms@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
