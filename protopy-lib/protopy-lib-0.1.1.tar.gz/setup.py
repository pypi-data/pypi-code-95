# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['protopy']

package_data = \
{'': ['*']}

install_requires = \
['Jinja2>=3.0.1,<4.0.0', 'cleo>=1.0.0a4,<2.0.0']

setup_kwargs = {
    'name': 'protopy-lib',
    'version': '0.1.1',
    'description': '',
    'long_description': 'None',
    'author': 'bennylut',
    'author_email': 'None',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
