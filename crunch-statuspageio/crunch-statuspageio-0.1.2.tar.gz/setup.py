# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['statuspageio']

package_data = \
{'': ['*']}

install_requires = \
['munch>=2.5.0,<3.0.0', 'requests>=2.26.0,<3.0.0']

setup_kwargs = {
    'name': 'crunch-statuspageio',
    'version': '0.1.2',
    'description': 'Python client library for statuspage.io',
    'long_description': None,
    'author': 'Adrien Pensart',
    'author_email': 'adrien.pensart@corp.ovh.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6',
}


setup(**setup_kwargs)
