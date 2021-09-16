# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['belette']

package_data = \
{'': ['*'], 'belette': ['licenses/*', 'templates/*']}

install_requires = \
['conan>=1.35.1,<2.0.0', 'docopt>=0.6.2,<0.7.0']

entry_points = \
{'console_scripts': ['belette = belette.belette:main']}

setup_kwargs = {
    'name': 'belette',
    'version': '0.1.0.dev2',
    'description': 'Generates licensing information for dependencies for Conan projects',
    'long_description': None,
    'author': 'Alazar Technologies Inc.',
    'author_email': 'support@alazartech.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
