# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['is_bcg_network']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['is_bcg_network = main:main']}

setup_kwargs = {
    'name': 'is-bcg-network',
    'version': '0.1.4',
    'description': 'one line import to know if you are running inside the BCG network',
    'long_description': None,
    'author': 'Niels Freier',
    'author_email': 'freier.niels@bcg.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
