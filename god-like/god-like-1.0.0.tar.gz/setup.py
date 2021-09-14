# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['god_like']

package_data = \
{'': ['*']}

install_requires = \
['Flask>=2.0.1,<3.0.0', 'Werkzeug>=2.0.1,<3.0.0']

setup_kwargs = {
    'name': 'god-like',
    'version': '1.0.0',
    'description': 'Flask for humans.',
    'long_description': None,
    'author': 'hostedposted',
    'author_email': 'hostedpostedsite@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/hostedposted/god-like/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
