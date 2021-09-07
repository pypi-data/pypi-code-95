# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['djdt_pev2', 'djdt_pev2.panels']

package_data = \
{'': ['*'], 'djdt_pev2': ['templates/djdt_pev2/panels/*']}

install_requires = \
['django-debug-toolbar>=3.2.0,<4.0.0']

setup_kwargs = {
    'name': 'djdt-pev2',
    'version': '0.1.0',
    'description': 'Django Debug Toolbar Postgress Exlain Visualizer 2 panel',
    'long_description': None,
    'author': 'william chu',
    'author_email': 'williamchu@uptickhq.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
