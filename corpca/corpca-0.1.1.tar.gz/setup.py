# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['corpca']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.21.2,<2.0.0', 'scikit-learn>=0.24.2,<0.25.0']

setup_kwargs = {
    'name': 'corpca',
    'version': '0.1.1',
    'description': '',
    'long_description': None,
    'author': 'Aiga SUZUKI',
    'author_email': 'tochikuji@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
