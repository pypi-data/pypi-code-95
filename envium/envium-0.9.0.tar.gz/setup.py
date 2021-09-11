# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['envium']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'envium',
    'version': '0.9.0',
    'description': '',
    'long_description': None,
    'author': 'Damian Krystkiewicz',
    'author_email': 'damian.krystkiewicz@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
