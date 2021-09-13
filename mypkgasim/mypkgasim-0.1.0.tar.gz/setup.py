# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mypkgasim']

package_data = \
{'': ['*']}

install_requires = \
['panda>=0.3.1,<0.4.0']

setup_kwargs = {
    'name': 'mypkgasim',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Your Name',
    'author_email': 'you@example.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
