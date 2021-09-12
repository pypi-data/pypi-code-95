# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['futurecandy', 'futurecandy.hooks']

package_data = \
{'': ['*']}

install_requires = \
['enquiries>=0.1.0,<0.2.0',
 'prompt-toolkit>=3.0.20,<4.0.0',
 'requests>=2.26.0,<3.0.0']

setup_kwargs = {
    'name': 'futurecandy',
    'version': '1.0',
    'description': 'Project initialization utility for Linux.',
    'long_description': None,
    'author': 'perpetualCreations',
    'author_email': 'tchen0584@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
