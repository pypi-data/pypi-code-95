# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cls_client', 'cls_client.ffi']

package_data = \
{'': ['*'], 'cls_client.ffi': ['libs/*']}

setup_kwargs = {
    'name': 'cls-client',
    'version': '1.3.0',
    'description': '',
    'long_description': None,
    'author': 'Dave Gaeddert',
    'author_email': 'dave.gaeddert@dropseed.dev',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
