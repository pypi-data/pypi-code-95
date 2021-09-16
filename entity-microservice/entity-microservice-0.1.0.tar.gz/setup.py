# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['entity_microservice']

package_data = \
{'': ['*']}

install_requires = \
['flask']

setup_kwargs = {
    'name': 'entity-microservice',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Sakshi Singla',
    'author_email': 'sakshi_singla@intuit.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
