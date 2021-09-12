# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['onebot']

package_data = \
{'': ['*']}

install_requires = \
['avilla-core>=0.0.12,<0.0.13']

setup_kwargs = {
    'name': 'avilla-onebot',
    'version': '0.0.7',
    'description': '',
    'long_description': None,
    'author': 'GreyElaina',
    'author_email': 'GreyElaina@outlook.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
