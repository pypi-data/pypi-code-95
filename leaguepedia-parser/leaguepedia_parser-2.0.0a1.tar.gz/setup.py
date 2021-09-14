# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['leaguepedia_parser',
 'leaguepedia_parser.parsers',
 'leaguepedia_parser.site',
 'leaguepedia_parser.transmuters']

package_data = \
{'': ['*']}

install_requires = \
['lol-dto>=2.0.0a4,<3.0.0',
 'lol-id-tools>=1.7.1,<2.0.0',
 'mwclient>=0.10.1,<0.11.0',
 'mwrogue>=0.0.14,<0.0.15']

setup_kwargs = {
    'name': 'leaguepedia-parser',
    'version': '2.0.0a1',
    'description': 'A parser for Leaguepedia data',
    'long_description': None,
    'author': 'Tolki',
    'author_email': 'gary.mialaret@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/mrtolkien/leaguepedia_parser',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
