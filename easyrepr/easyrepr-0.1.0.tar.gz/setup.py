# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['easyrepr']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'easyrepr',
    'version': '0.1.0',
    'description': 'Python decorator to automatically generate repr strings',
    'long_description': None,
    'author': 'Chris Bouchard',
    'author_email': 'chris@upliftinglemma.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/chrisbouchard/autorepr',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
