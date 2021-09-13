# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': '.'}

packages = \
['textalytics_client']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.26.0,<3.0.0', 'textalytics-core>=0.1.1,<0.2.0']

entry_points = \
{'console_scripts': ['test = scripts:test']}

setup_kwargs = {
    'name': 'textalytics-python-client',
    'version': '0.1.0',
    'description': 'python client to interface with textalytics hosted nlp',
    'long_description': None,
    'author': 'Manoj Bharadwaj',
    'author_email': 'manoj@cloudcosmos.tech',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
