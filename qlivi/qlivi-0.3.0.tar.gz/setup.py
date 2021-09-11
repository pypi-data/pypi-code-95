# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['qlivi', 'qlivi.cli']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.1,<9.0.0', 'pandas>=1.3.2,<2.0.0', 'requests>=2.26.0,<3.0.0']

setup_kwargs = {
    'name': 'qlivi',
    'version': '0.3.0',
    'description': 'dd',
    'long_description': None,
    'author': 'musangtara',
    'author_email': 'musangtara@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<4.0.0',
}


setup(**setup_kwargs)
