# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['assault_and_battery']

package_data = \
{'': ['*']}

install_requires = \
['matplotlib>=3.4.3,<4.0.0', 'pyserial>=3.5,<4.0']

entry_points = \
{'console_scripts': ['assault = assault_and_battery.cli:cli']}

setup_kwargs = {
    'name': 'assault-and-battery',
    'version': '0.1.0',
    'description': 'A battery discharge curve calculator slash torture test.',
    'long_description': None,
    'author': 'Stavros Korokithakis',
    'author_email': 'hi@stavros.io',
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
