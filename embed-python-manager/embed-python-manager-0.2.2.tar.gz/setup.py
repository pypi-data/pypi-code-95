# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['embed_python_manager']

package_data = \
{'': ['*'], 'embed_python_manager': ['source_list/*']}

install_requires = \
['lk-logger>=4.0.0', 'lk-utils>=2.0.0b0', 'pyyaml']

setup_kwargs = {
    'name': 'embed-python-manager',
    'version': '0.2.2',
    'description': 'Download and manage embedded python versions.',
    'long_description': None,
    'author': 'Likianta',
    'author_email': 'likianta@foxmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8',
}


setup(**setup_kwargs)
