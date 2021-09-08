# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['typed_graphql']

package_data = \
{'': ['*']}

install_requires = \
['graphql-core>=3.1.2,<4.0.0']

setup_kwargs = {
    'name': 'typed-graphql',
    'version': '0.10.0',
    'description': 'Use types to have a simpler graphql implementation',
    'long_description': None,
    'author': 'Willem Thiart',
    'author_email': 'himself@willemthiart.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
