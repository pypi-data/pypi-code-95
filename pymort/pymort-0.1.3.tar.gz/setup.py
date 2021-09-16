# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pymort', 'pymort.SOA_Tables_20210915']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'pymort',
    'version': '0.1.3',
    'description': '',
    'long_description': None,
    'author': 'Matthew Caseres',
    'author_email': 'matthewcaseres@outlook.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
