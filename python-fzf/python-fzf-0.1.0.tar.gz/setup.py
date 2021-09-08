# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fzf']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'python-fzf',
    'version': '0.1.0',
    'description': 'Python wrapper for fzf.',
    'long_description': None,
    'author': 'samedamci',
    'author_email': 'samedamci@disroot.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9.2,<4.0.0',
}


setup(**setup_kwargs)
