# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mikro', 'mikro.graphql', 'mikro.graphql.mutations', 'mikro.graphql.queries']

package_data = \
{'': ['*']}

install_requires = \
['docstring-parser>=0.10,<0.11',
 'herre==0.1.2',
 'inflection>=0.5.1,<0.6.0',
 's3fs>=2021.8.1,<2022.0.0',
 'xarray>=0.19.0,<0.20.0']

setup_kwargs = {
    'name': 'mikro',
    'version': '0.1.3',
    'description': 'images for arnheim',
    'long_description': None,
    'author': 'jhnnsrs',
    'author_email': 'jhnnsrs@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
