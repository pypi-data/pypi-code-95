# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['poetryup']

package_data = \
{'': ['*']}

install_requires = \
['tomlkit>=0.7.2,<0.8.0']

entry_points = \
{'console_scripts': ['poetryup = poetryup.poetryup:main']}

setup_kwargs = {
    'name': 'poetryup',
    'version': '0.3.2',
    'description': 'Update dependencies and bump their version in the pyproject.toml file',
    'long_description': "# PoetryUp\n\n![build](https://github.com/MousaZeidBaker/poetryup/workflows/Publish/badge.svg)\n![test](https://github.com/MousaZeidBaker/poetryup/workflows/Test/badge.svg)\n[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)\n![python_version](https://img.shields.io/badge/python-%3E=3.6-blue.svg)\n[![pypi_v](https://img.shields.io/pypi/v/poetryup.svg)](https://pypi.org/project/poetryup)\n[![pypi_dm](https://img.shields.io/pypi/dm/poetryup.svg)](https://pypi.org/project/poetryup)\n\nPoetryUp updates dependencies and bumps their version in the `pyproject.toml` file with respect to their version\nconstraint. The `poetry.lock` file will be recreated as well. PoetryUp runs\n[poetry](https://github.com/python-poetry/poetry) commands, thus it's required to be installed. The difference between\nrunning `poetry update` and `poetryup`, is that the latter also modifies the `pyproject.toml` file.\n\n## Usage\n```shell\npoetryup\n```\n\n## Test\nActivate virtualenv & Install project dependencies\n```shell\npoetry shell && poetry install\n```\n\nRun tests\n```shell\npytest tests\n```\n\n## Contributing\nContributions are welcome via pull requests.\n\n## Issues\nIf you encounter any problems, please file an [issue](https://github.com/MousaZeidBaker/poetryup/issues) along with a\ndetailed description.\n",
    'author': 'Mousa Zeid Baker',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/MousaZeidBaker/poetryup',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
