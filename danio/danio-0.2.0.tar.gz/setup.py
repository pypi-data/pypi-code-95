# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['danio']

package_data = \
{'': ['*']}

install_requires = \
['databases>=0.4.3,<0.5.0']

setup_kwargs = {
    'name': 'danio',
    'version': '0.2.0',
    'description': 'Lightly ORM',
    'long_description': None,
    'author': 'strongbugman',
    'author_email': 'strongbugman@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
