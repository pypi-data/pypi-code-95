# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['crostab',
 'crostab.convert',
 'crostab.crostab',
 'crostab.enum',
 'crostab.enum.keys',
 'crostab.series',
 'crostab.structs',
 'crostab.table',
 'crostab.types',
 'crostab.utils']

package_data = \
{'': ['*']}

install_requires = \
['aryth>=0.0.12', 'ject>=0.0.3', 'veho>=0.0.10']

setup_kwargs = {
    'name': 'crostab',
    'version': '0.0.10',
    'description': 'cross table analytical tool',
    'long_description': None,
    'author': 'hazen',
    'author_email': 'hoyeungw@outlook.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
