# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['lok',
 'lok.bouncer',
 'lok.management',
 'lok.management.commands',
 'lok.middlewares',
 'lok.middlewares.request',
 'lok.middlewares.scope',
 'lok.migrations']

package_data = \
{'': ['*']}

install_requires = \
['Django>=3.2.7,<4.0.0', 'PyJWT>=2.1.0,<3.0.0']

setup_kwargs = {
    'name': 'lok',
    'version': '0.1.3',
    'description': 'lok is a jwt middleware that works with django channels',
    'long_description': None,
    'author': 'jhnnsrs',
    'author_email': 'jhnnsrs@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
