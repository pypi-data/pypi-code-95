# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aurorax', 'aurorax._internal']

package_data = \
{'': ['*']}

install_requires = \
['aacgmv2>=2.6.2,<3.0.0',
 'flake8>=3.8.4,<4.0.0',
 'humanize>=3.2.0,<4.0.0',
 'pydantic>=1.7.3,<2.0.0',
 'requests>=2.25.1,<3.0.0']

setup_kwargs = {
    'name': 'pyaurorax',
    'version': '0.6.5',
    'description': 'Python library for interacting with the AuroraX API',
    'long_description': '# PyAuroraX\n\n[![Github Actions - Tests](https://github.com/aurorax-space/pyaurorax/workflows/tests/badge.svg)](https://github.com/aurorax-space/pyaurorax/actions?query=workflow%3Atests)\n[![PyPI version](https://img.shields.io/pypi/v/pyaurorax.svg)](https://pypi.python.org/pypi/pyaurorax/)\n[![MIT license](https://img.shields.io/badge/License-MIT-blue.svg)](https://lbesson.mit-license.org/)\n[![PyPI Python versions](https://img.shields.io/pypi/pyversions/pyaurorax.svg)](https://pypi.python.org/pypi/pyaurorax/)\n\nPython library for interacting with the AuroraX API.\n\n## Installing PyAuroraX\n\nPyAuroraX is available on PyPI:\n\n```console\n$ python -m pip install pyaurorax\n```\n\n## Supported Python Versions\n\nPyAuroraX officially supports Python 3.6+.\n\n## Usage\n\n```python\n>>> import aurorax\n```\n\n## Development\n\nClone the repository and install dependencies using Poetry.\n\n```console\n$ git clone https://github.com/aurorax-space/pyaurorax.git\n$ cd pyaurorax\n$ make install\n```\n\n## Testing\n\n```console\n$ make test\n[ or do each test separately ]\n$ make test-flake8\n$ make test-pylint\n$ make test-bandit\n$ make test-pytest\n```\n\n## Additional Testing for Development Environments\n\nTo run additional tests that are not integrated into the CI pipeline, run the following:\n\n```console\n$ make test-additional\n```\n',
    'author': 'Darren Chaddock',
    'author_email': 'dchaddoc@ucalgary.ca',
    'maintainer': 'Darren Chaddock',
    'maintainer_email': 'dchaddoc@ucalgary.ca',
    'url': 'https://github.com/aurorax-space/pyaurorax',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
