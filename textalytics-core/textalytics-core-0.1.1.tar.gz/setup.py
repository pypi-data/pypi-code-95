# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['textalytics_core']

package_data = \
{'': ['*']}

install_requires = \
['pydantic>=1.8.2,<2.0.0']

entry_points = \
{'console_scripts': ['test = scripts:test']}

setup_kwargs = {
    'name': 'textalytics-core',
    'version': '0.1.1',
    'description': 'core textalytics capabilities',
    'long_description': None,
    'author': 'Manoj Bharadwaj',
    'author_email': 'manoj@cloudcosmos.tech',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
