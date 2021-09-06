# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['is_bcg_network']

package_data = \
{'': ['*']}

install_requires = \
['ntplib>=0.4.0,<0.5.0']

entry_points = \
{'console_scripts': ['is_bcg_network = main:main']}

setup_kwargs = {
    'name': 'is-bcg-network',
    'version': '0.1.3',
    'description': 'one line import to know if you are running inside the BCG network',
    'long_description': None,
    'author': 'Niels Freier',
    'author_email': 'freier.niels@bcg.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
