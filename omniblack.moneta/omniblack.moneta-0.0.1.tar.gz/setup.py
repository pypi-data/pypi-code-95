# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['omniblack', 'omniblack.moneta']

package_data = \
{'': ['*']}

install_requires = \
['GitPython>=3.1.15,<4.0.0',
 'anyio>=3.0.1,<4.0.0',
 'attrs>=20.3.0,<21.0.0',
 'more-itertools>=8.8.0,<9.0.0',
 'omniblack.repo>=0.0.1,<0.0.2',
 'parver>=0.3.1,<0.4.0',
 'ruamel.yaml>=0.16.0,<0.17.0']

setup_kwargs = {
    'name': 'omniblack.moneta',
    'version': '0.0.1',
    'description': 'A changelog manager for omniblack.',
    'long_description': None,
    'author': 'Terry Patterson',
    'author_email': 'Terryp@wegrok.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
