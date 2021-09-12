# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyportable_crypto']

package_data = \
{'': ['*']}

install_requires = \
['pycryptodomex']

setup_kwargs = {
    'name': 'pyportable-crypto',
    'version': '0.1.0',
    'description': 'Crypto compiler for Pyportable-Installer project.',
    'long_description': None,
    'author': 'Likianta',
    'author_email': 'likianta@foxmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3',
}


setup(**setup_kwargs)
