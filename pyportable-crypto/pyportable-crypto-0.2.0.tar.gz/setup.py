# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyportable_crypto', 'pyportable_crypto.key_machine']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'pyportable-crypto',
    'version': '0.2.0',
    'description': 'Crypto plugin for pyportable-installer project.',
    'long_description': None,
    'author': 'Likianta',
    'author_email': 'likianta@foxmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6',
}


setup(**setup_kwargs)
