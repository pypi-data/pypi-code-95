# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['odoo_stubs']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'odoo-stubs',
    'version': '0.1.dev0',
    'description': 'Project description',
    'long_description': None,
    'author': 'Dmitry Voronin',
    'author_email': 'dmitry665@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/voronind/odoo-stubs',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
