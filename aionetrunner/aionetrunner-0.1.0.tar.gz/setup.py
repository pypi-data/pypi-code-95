# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['netrunner',
 'netrunner.connections',
 'netrunner.host',
 'netrunner.runner',
 'netrunner.task']

package_data = \
{'': ['*']}

install_requires = \
['asyncssh>=2.7.0,<3.0.0',
 'genie>=21.8,<22.0',
 'pyats>=21.8,<22.0',
 'scrapli>=2021.1.30,<2022.0.0']

setup_kwargs = {
    'name': 'aionetrunner',
    'version': '0.1.0',
    'description': 'Network asyncio command runner using Scrapli',
    'long_description': None,
    'author': 'Ryan Bradshaw',
    'author_email': 'ryan@rbradshaw.dev',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
