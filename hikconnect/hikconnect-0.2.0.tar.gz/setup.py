# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['hikconnect']

package_data = \
{'': ['*']}

install_requires = \
['httpx>=0.19.0,<0.20.0']

setup_kwargs = {
    'name': 'hikconnect',
    'version': '0.2.0',
    'description': 'Communicate with Hikvision smart doorbells via Hik-Connect cloud.',
    'long_description': '',
    'author': 'Tomas Bedrich',
    'author_email': 'ja@tbedrich.cz',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://pypi.org/project/hikconnect',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
