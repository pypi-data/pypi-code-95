# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['planetwatch']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.1', 'pycoingecko>=2.2.0,<3.0.0']

entry_points = \
{'console_scripts': ['planets = planetwatch.core:cli']}

setup_kwargs = {
    'name': 'planetwatch',
    'version': '0.1.0',
    'description': 'Code to make it easy to caluculate earnings, etc for planetwatch',
    'long_description': None,
    'author': 'errantp',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
