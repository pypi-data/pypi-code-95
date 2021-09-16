# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ou_sphinx_a11y']

package_data = \
{'': ['*']}

install_requires = \
['sphinx>=4.2.0,<5.0.0']

entry_points = \
{'sphinx.builders': ['a11ycheck = ou_sphinx_a11y']}

setup_kwargs = {
    'name': 'ou-sphinx-a11y',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Mark Hall',
    'author_email': 'mark.hall@open.ac.uk',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
