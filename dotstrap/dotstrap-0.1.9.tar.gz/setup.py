# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dotstrap']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.1,<9.0.0', 'pexpect>=4.8.0,<5.0.0']

entry_points = \
{'console_scripts': ['dotstrap = dotstrap.dotstrap:cli']}

setup_kwargs = {
    'name': 'dotstrap',
    'version': '0.1.9',
    'description': 'A simiple Python based command line tool that acts as a git wrapper for simplifying dotfile management via bare git repository.',
    'long_description': None,
    'author': 'mark',
    'author_email': 'mark@dixon.se',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
