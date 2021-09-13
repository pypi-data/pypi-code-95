# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['d_py']

package_data = \
{'': ['*']}

install_requires = \
['discord.py>=1.7.3,<2.0.0']

setup_kwargs = {
    'name': 'd-py',
    'version': '0.0.2',
    'description': 'helper package for discord.py processes',
    'long_description': None,
    'author': 'Andrew Bordis',
    'author_email': 'andrewbordis111@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
