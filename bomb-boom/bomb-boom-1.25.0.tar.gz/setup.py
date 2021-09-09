# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': '.'}

packages = \
['bomb']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'bomb-boom',
    'version': '1.25.0',
    'description': 'Bomb package',
    'long_description': None,
    'author': 'Nikita Barinov',
    'author_email': 'diadorer@yandex.ru',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
