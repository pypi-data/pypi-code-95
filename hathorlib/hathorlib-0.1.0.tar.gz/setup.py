# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['hathorlib', 'hathorlib.conf']

package_data = \
{'': ['*']}

install_requires = \
['base58>=2.1.0', 'cryptography>=3.3.1']

extras_require = \
{'client': ['structlog>=20.0.0', 'aiohttp>=3.7.0']}

setup_kwargs = {
    'name': 'hathorlib',
    'version': '0.1.0',
    'description': 'Hathor Network base objects library',
    'long_description': 'hathorlib\n=========\n\nHathor Network base library.\n\nCurrently this is a placeholder, the actual library will be here soon.\n',
    'author': 'Hathor Team',
    'author_email': 'contact@hathor.network',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://hathor.network/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
