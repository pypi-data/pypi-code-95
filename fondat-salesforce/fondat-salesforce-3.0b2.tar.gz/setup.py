# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fondat', 'fondat.salesforce']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.7,<4.0', 'fondat-core>=3.0,<4.0']

setup_kwargs = {
    'name': 'fondat-salesforce',
    'version': '3.0b2',
    'description': 'Fondat package for Salesforce.',
    'long_description': '# fondat-salesforce\n\n[![PyPI](https://badge.fury.io/py/fondat-salesforce.svg)](https://badge.fury.io/py/fondat-salesforce)\n[![License](https://img.shields.io/github/license/fondat/fondat-salesforce.svg)](https://github.com/fondat/fondat-salesforce/blob/main/LICENSE)\n[![GitHub](https://img.shields.io/badge/github-main-blue.svg)](https://github.com/fondat/fondat-salesforce/)\n[![Test](https://github.com/fondat/fondat-salesforce/workflows/test/badge.svg)](https://github.com/fondat/fondat-salesforce/actions?query=workflow/test)\n[![Black](https://img.shields.io/badge/code%20style-black-black.svg)](https://github.com/psf/black)\n\nFondat package for Salesforce.\n\n## Develop\n\n```\npoetry install\npoetry run pre-commit install\n```\n\n## Test\n\n```\npoetry run pytest\n```\n',
    'author': 'fondat-salesforce authors',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/fondat/fondat-salesforce/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
