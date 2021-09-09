# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['knex']

package_data = \
{'': ['*']}

install_requires = \
['regex>=2021.8.28,<2022.0.0']

setup_kwargs = {
    'name': 'knex',
    'version': '0.1.1',
    'description': 'Python library for building composable text parsers',
    'long_description': '# knex\nPython library for creating chainable text parsers\n',
    'author': 'Clay Curtis',
    'author_email': 'clay584@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/clay584/knex',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
