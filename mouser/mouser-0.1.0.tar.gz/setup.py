# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mouser']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0,<9.0', 'requests>=2.26,<3.0']

entry_points = \
{'console_scripts': ['mouser = mouser.cli:mouser_cli']}

setup_kwargs = {
    'name': 'mouser',
    'version': '0.1.0',
    'description': '',
    'long_description': '# Mouser Python API\n\n## Setup\n### Mouser API Keys\n\nTBD\n\n### Install\n\nTBD\n\n## Usage\n\nTBD',
    'author': 'eeintech',
    'author_email': 'eeintech@eeinte.ch',
    'maintainer': 'eeintech',
    'maintainer_email': 'eeintech@eeinte.ch',
    'url': 'https://github.com/sparkmicro/mouser',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
