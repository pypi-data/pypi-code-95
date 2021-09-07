# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['jrtimeman']

package_data = \
{'': ['*']}

install_requires = \
['beautiful-date>=2.0.0,<3.0.0',
 'gcsa>=1.2.0,<2.0.0',
 'google>=3.0.0,<4.0.0',
 'matplotlib>=3.4.3,<4.0.0',
 'numpy>=1.21.2,<2.0.0',
 'pandas>=1.3.2,<2.0.0']

setup_kwargs = {
    'name': 'jrtimeman',
    'version': '0.2.0',
    'description': 'Jumping Rivers: Time Management',
    'long_description': None,
    'author': 'Jack Walton',
    'author_email': 'jwalton3141@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<3.11',
}


setup(**setup_kwargs)
