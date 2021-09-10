# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['scatsol']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'scatsol',
    'version': '0.0.1',
    'description': '',
    'long_description': None,
    'author': 'tiagovla',
    'author_email': 'tiagovla@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
