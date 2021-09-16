# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['test-service-iks']

package_data = \
{'': ['*']}

install_requires = \
['Flask>=2.0.1,<3.0.0']

setup_kwargs = {
    'name': 'test-service-iks',
    'version': '0.1.2',
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
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
