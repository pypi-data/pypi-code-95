# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['proxy_validator']

package_data = \
{'': ['*']}

install_requires = \
['PySocks>=1.7.1,<2.0.0', 'requests>=2.24.0']

setup_kwargs = {
    'name': 'proxy-validator',
    'version': '0.2.5',
    'description': 'Utility for proxy validation',
    'long_description': None,
    'author': 'nash',
    'author_email': 'nash@fixmost.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>3.6',
}


setup(**setup_kwargs)
