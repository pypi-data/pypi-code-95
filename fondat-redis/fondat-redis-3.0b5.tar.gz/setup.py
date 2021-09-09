# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fondat']

package_data = \
{'': ['*']}

install_requires = \
['aioredis>=2.0,<3.0', 'fondat-core>=3.0,<4.0']

setup_kwargs = {
    'name': 'fondat-redis',
    'version': '3.0b5',
    'description': 'Fondat module for Redis.',
    'long_description': '# fondat-redis\n\n[![PyPI](https://badge.fury.io/py/fondat-redis.svg)](https://badge.fury.io/py/fondat-redis)\n[![License](https://img.shields.io/github/license/fondat/fondat-redis.svg)](https://github.com/fondat/fondat-redis/blob/main/LICENSE)\n[![GitHub](https://img.shields.io/badge/github-main-blue.svg)](https://github.com/fondat/fondat-redis/)\n[![Test](https://github.com/fondat/fondat-redis/workflows/test/badge.svg)](https://github.com/fondat/fondat-redis/actions?query=workflow/test)\n[![Black](https://img.shields.io/badge/code%20style-black-black.svg)](https://github.com/psf/black)\n\nFondat module for Redis.\n\n## Develop\n\n```\npoetry install\npoetry run pre-commit install\n```\n\n## Test\n\n```\npoetry run pytest\n```\n',
    'author': 'fondat-redis authors',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/fondat/fondat-redis/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
