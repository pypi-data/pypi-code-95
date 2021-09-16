# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['arcane']

package_data = \
{'': ['*']}

install_requires = \
['arcane-core>=1.0.10,<2.0.0',
 'arcane-requests>=0.1.1,<0.2.0',
 'backoff>=1.10.0,<2.0.0',
 'requests>=2.23.0,<3.0.0']

setup_kwargs = {
    'name': 'arcane-clients',
    'version': '1.1.2',
    'description': 'Utility functions to interact with our clients_service',
    'long_description': '# Arcane clients\n\nThis package helps us to request our clients_service\n',
    'author': 'Arcane',
    'author_email': 'product@arcane.run',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
