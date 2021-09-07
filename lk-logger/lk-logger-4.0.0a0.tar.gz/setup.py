# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['lk_logger',
 'lk_logger.config',
 'lk_logger.plugins',
 'lk_logger.scanner',
 'lk_logger.terminals']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'lk-logger',
    'version': '4.0.0a0',
    'description': 'Advanced and easy-to-use Python logger that prints with varnames.',
    'long_description': None,
    'author': 'Likianta',
    'author_email': 'likianta@foxmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
