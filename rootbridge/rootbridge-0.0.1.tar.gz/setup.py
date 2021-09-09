# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['rootbridge']

package_data = \
{'': ['*']}

install_requires = \
['sh>=1.14.2,<2.0.0', 'understory>=0.0.67,<0.0.68']

setup_kwargs = {
    'name': 'rootbridge',
    'version': '0.0.1',
    'description': 'Bridge to the social networks.',
    'long_description': None,
    'author': 'Angelo Gladding',
    'author_email': 'angelo@lahacker.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<3.10',
}


setup(**setup_kwargs)
