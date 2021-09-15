# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['poetryupvers']

package_data = \
{'': ['*']}

install_requires = \
['docopt>=0.6.2,<0.7.0',
 'gitlab-ps-utils>=0.1.4,<0.2.0',
 'semver>=2.13.0,<3.0.0',
 'tomlkit>=0.7.2,<0.8.0']

entry_points = \
{'console_scripts': ['ppuv = poetryupvers.main:run']}

setup_kwargs = {
    'name': 'poetryupvers',
    'version': '0.1.0',
    'description': 'Semantic versioning on a pyproject.toml',
    'long_description': None,
    'author': 'Michael Leopard',
    'author_email': 'mleopard@gitlab.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<3.9',
}


setup(**setup_kwargs)
