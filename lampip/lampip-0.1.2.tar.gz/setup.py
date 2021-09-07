# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['lampip', 'lampip.core']

package_data = \
{'': ['*']}

install_requires = \
['boto3', 'click', 'sh', 'termcolor', 'toml']

entry_points = \
{'console_scripts': ['lampip = lampip.entrypoint:main']}

setup_kwargs = {
    'name': 'lampip',
    'version': '0.1.2',
    'description': 'Simple CLI tool for creating custom python lambda layers',
    'long_description': None,
    'author': 'hayashiya18',
    'author_email': 'sei8haya@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/hayashiya18/lampip',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
