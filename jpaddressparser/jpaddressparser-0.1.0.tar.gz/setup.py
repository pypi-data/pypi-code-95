# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['jpaddressparser']

package_data = \
{'': ['*']}

install_requires = \
['jaconv>=0.3,<0.4', 'marisa-trie>=0.7.7,<0.8.0', 'requests>=2.26.0,<3.0.0']

setup_kwargs = {
    'name': 'jpaddressparser',
    'version': '0.1.0',
    'description': 'Parser for Japanese Addresses',
    'long_description': None,
    'author': 'Du Shiqiao',
    'author_email': 'lucidfrontier.45@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4',
}


setup(**setup_kwargs)
