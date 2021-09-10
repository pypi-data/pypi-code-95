# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['views_partitioning']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'views-partitioning',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'peder2911',
    'author_email': 'pglandsverk@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
