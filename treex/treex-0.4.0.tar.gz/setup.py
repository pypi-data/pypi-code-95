# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['treex', 'treex.nn']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=5.4.1,<6.0.0',
 'flax>=0.3.4,<0.4.0',
 'jax>=0.2.18,<0.3.0',
 'jaxlib>=0.1.70,<0.2.0',
 'optax>=0.0.9,<0.0.10',
 'rich>=10.7.0,<11.0.0']

setup_kwargs = {
    'name': 'treex',
    'version': '0.4.0',
    'description': '',
    'long_description': None,
    'author': 'Cristian Garcia',
    'author_email': 'cgarcia.e88@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
