# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['thlink_backend_db_lib']

package_data = \
{'': ['*']}

install_requires = \
['boto3>=1.17.78,<2.0.0', 'circuitbreaker>=1.3.1,<2.0.0']

setup_kwargs = {
    'name': 'thlink-backend-db-lib',
    'version': '0.4.10',
    'description': 'Dynamodb Wrapper',
    'long_description': None,
    'author': 'thlink',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
