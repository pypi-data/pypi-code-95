# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['views_dataviz']

package_data = \
{'': ['*']}

install_requires = \
['matplotlib>=3.4.3,<4.0.0', 'pandas>=1.3.2,<2.0.0']

setup_kwargs = {
    'name': 'views-dataviz',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'peder2911',
    'author_email': 'pglandsverk@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
