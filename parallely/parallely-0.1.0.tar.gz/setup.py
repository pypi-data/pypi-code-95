# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['parallely']

package_data = \
{'': ['*']}

install_requires = \
['asyncio>=3.4.3,<4.0.0', 'nest-asyncio>=1.5.1,<2.0.0', 'pathos>=0.2.8,<0.3.0']

setup_kwargs = {
    'name': 'parallely',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Mikkel Vilstrup',
    'author_email': 'mikkel@vilstrup.dk',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<3.11',
}


setup(**setup_kwargs)
