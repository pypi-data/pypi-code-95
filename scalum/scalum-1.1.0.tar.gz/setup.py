# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['scalum']

package_data = \
{'': ['*']}

install_requires = \
['numpy']

setup_kwargs = {
    'name': 'scalum',
    'version': '1.1.0',
    'description': '',
    'long_description': None,
    'author': 'Oguz Vuruskaner',
    'author_email': 'ovuruska@outlook.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
