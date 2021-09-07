# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['frage']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.7.4,<4.0.0', 'dhall>=0.1.7,<0.2.0', 'pydantic>=1.8.2,<2.0.0']

entry_points = \
{'console_scripts': ['frage = frage.__main__:run']}

setup_kwargs = {
    'name': 'frage',
    'version': '0.2.0',
    'description': 'Make pre-configured requests from the commandline',
    'long_description': 'About\n---\nMake pre-configured requests from the command line.\n\n\nAuthor\n---\n\nElias Tandel < elias.tandel at gmail >\n',
    'author': 'Elias Tandel',
    'author_email': 'elias.tandel@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/etandel/frage',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
