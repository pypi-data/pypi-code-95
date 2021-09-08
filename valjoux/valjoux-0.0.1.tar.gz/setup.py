# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['valjoux', 'valjoux.convert', 'valjoux.eta', 'valjoux.strategies']

package_data = \
{'': ['*']}

install_requires = \
['aryth>=0.0.12', 'crostab>=0.0.11', 'veho>=0.0.10']

setup_kwargs = {
    'name': 'valjoux',
    'version': '0.0.1',
    'description': '',
    'long_description': None,
    'author': 'hazen',
    'author_email': 'hoyeungw@outlook.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
