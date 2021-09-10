# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aiomusiccast']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.7.4,<4.0.0']

setup_kwargs = {
    'name': 'aiomusiccast',
    'version': '0.9.2',
    'description': 'Companion library for musiccast devices intended for the Home Assistant integration.',
    'long_description': '<div align="center">\n\n<picture>\n  <source srcset="banner-dark.png" media="(prefers-color-scheme: dark)">\n  <img src="banner.png">\n</picture>\n\n## Companion library for musiccast devices intended for the Home Assistant integration.\n\n[![PyPI Version](https://img.shields.io/pypi/v/aiomusiccast.svg)](https://pypi.org/project/aiomusiccast)\n![GitHub release (latest by date)](https://img.shields.io/github/v/release/vigonotion/aiomusiccast)\n![Read the Docs](https://img.shields.io/readthedocs/aiomusiccast)\n[![PyPI License](https://img.shields.io/pypi/l/aiomusiccast.svg)](https://pypi.org/project/aiomusiccast)\n\n\n</div>\n\n<br/>\n\n# Setup\n\n## Requirements\n\n* Python 3.8+\n\n## Installation\n\nInstall it directly into an activated virtual environment:\n\n```text\n$ pip install aiomusiccast\n```\n\nor add it to your [Poetry](https://poetry.eustace.io/) project:\n\n```text\n$ poetry add aiomusiccast\n```\n\n# Usage\n\nAfter installation, the package can imported:\n\n```text\n$ python\n>>> import aiomusiccast\n>>> aiomusiccast.__version__\n```\n',
    'author': 'Tom Schneider',
    'author_email': 'mail@vigonotion.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://pypi.org/project/aiomusiccast',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
