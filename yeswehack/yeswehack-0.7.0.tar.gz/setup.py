# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['yeswehack']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.24.0,<3.0.0']

setup_kwargs = {
    'name': 'yeswehack',
    'version': '0.7.0',
    'description': 'yeswehack - YesWeHack API Wrapper',
    'long_description': 'SDK for yeswehack\n\n\n# Build from source\n\n`make build` (or `poetry build`)\n\n# Installation\n\n## Developer\n\n### Requirements\n\n- [`poetry`](https://python-poetry.org/) (`pip install poetry`)\n\n### Installation\n\n`make install` (or `poetry install`): creates a virtualenv and install dependencies\n\n## From pip\n\n```\npip install yeswehack\n```\n\n## From wheel\n\n```\npip install path/to/yeswehack-wheel.whl\n```\n\n# Getting starting with YesWeHack Python SDK\n\n## API Module\n\nIn this python module, we define object mapping to YesWeHack API Object.\n',
    'author': 'Jean Lou Hau',
    'author_email': 'jl.hau@yeswehack.com',
    'maintainer': 'YesWeHack',
    'maintainer_email': 'project@yeswehack.com',
    'url': 'https://yeswehack.com',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.0,<3.10',
}


setup(**setup_kwargs)
