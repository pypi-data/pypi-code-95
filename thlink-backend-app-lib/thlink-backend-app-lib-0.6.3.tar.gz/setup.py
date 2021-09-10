# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['thlink_backend_app_lib']

package_data = \
{'': ['*']}

install_requires = \
['aws-lambda-powertools>=1.16,<2.0', 'pydantic>=1.8.2,<2.0.0']

setup_kwargs = {
    'name': 'thlink-backend-app-lib',
    'version': '0.6.3',
    'description': '',
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
