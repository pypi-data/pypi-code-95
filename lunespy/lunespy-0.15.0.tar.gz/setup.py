# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['lunespy',
 'lunespy.client',
 'lunespy.client.transactions',
 'lunespy.client.transactions.transfer_asset',
 'lunespy.client.wallet',
 'lunespy.server',
 'lunespy.server.address',
 'lunespy.utils',
 'lunespy.utils.crypto',
 'lunespy.utils.settings']

package_data = \
{'': ['*']}

install_requires = \
['base58>=2.1.0,<3.0.0',
 'pyblake2>=1.1.2,<2.0.0',
 'python-axolotl-curve25519>=0.4.1.post2,<0.5.0',
 'requests>=2.26.0,<3.0.0']

setup_kwargs = {
    'name': 'lunespy',
    'version': '0.15.0',
    'description': 'Library for communication with nodes in mainnet or testnet of the lunes-blockchain network',
    'long_description': None,
    'author': 'Lunes Platform',
    'author_email': 'lucas.oliveira@lunes.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
