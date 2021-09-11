# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fondat']

package_data = \
{'': ['*']}

install_requires = \
['aiosqlite>=0.16,<0.17',
 'iso8601>=0.1,<0.2',
 'multidict>=5.1,<6.0',
 'wrapt>=1.12,<2.0']

setup_kwargs = {
    'name': 'fondat-core',
    'version': '3.0.1',
    'description': 'A foundation for asynchronous Python resource-oriented applications.',
    'long_description': '# fondat-core\n\n[![PyPI](https://img.shields.io/pypi/v/fondat-core)](https://pypi.org/project/fondat-core/)\n[![Python](https://img.shields.io/pypi/pyversions/fondat-core)](https://python.org/)\n[![GitHub](https://img.shields.io/badge/github-main-blue.svg)](https://github.com/fondat/fondat-core/)\n[![Test](https://github.com/fondat/fondat-core/workflows/test/badge.svg)](https://github.com/fondat/fondat-core/actions?query=workflow/test)\n[![License](https://img.shields.io/github/license/fondat/fondat-core.svg)](https://github.com/fondat/fondat-core/blob/main/LICENSE)\n[![Black](https://img.shields.io/badge/code%20style-black-black.svg)](https://github.com/psf/black)\n\nA foundation for Python resource-oriented applications. \n\n## Introduction\n\nFondat is a foundation for building resource-oriented applications in Python.\nBy composing your application as a set of resources that expose operations,\nthey can be automatically exposed through an HTTP API.\n\n## Features\n\n* Asynchronous uniform resource interface.\n* Resource operations can be exposed through HTTP API.\n* Type encoding and validation of resource operation parameters and return values.\n* Authorization to resource operations enforced through security policies.\n* Abstraction of SQL tables, indexes and queries.\n* Monitoring of resource operations and elapsed time in time series databases.\n* Generates [OpenAPI](https://www.openapis.org/) documents, compatible with [Swagger UI](https://swagger.io/tools/swagger-ui/).\n\n## Install\n\n```\npip install fondat-core\n```\n\n## Develop\n\n```\npoetry install\npoetry run pre-commit install\n```\n\n## Test\n\n```\npoetry run pytest\n```\n',
    'author': 'fondat-core authors',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/fondat/fondat/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
