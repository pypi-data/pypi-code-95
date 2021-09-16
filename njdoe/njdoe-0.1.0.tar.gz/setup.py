# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['njdoe']

package_data = \
{'': ['*']}

install_requires = \
['beautifulsoup4>=4.10.0,<5.0.0', 'requests>=2.26.0,<3.0.0']

setup_kwargs = {
    'name': 'njdoe',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Charlie Bini',
    'author_email': 'cbini87@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
