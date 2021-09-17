# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['indieauth']

package_data = \
{'': ['*']}

install_requires = \
['understory>=0.0.71,<0.0.72']

setup_kwargs = {
    'name': 'indieauth',
    'version': '0.0.1',
    'description': '',
    'long_description': None,
    'author': 'Angelo Gladding',
    'author_email': 'self@angelogladding.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<3.10',
}


setup(**setup_kwargs)
