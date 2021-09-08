# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['yearmonth']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'yearmonth',
    'version': '0.1.0',
    'description': 'A pydantic compatible yearmonth datatype',
    'long_description': None,
    'author': 'bsnacks000',
    'author_email': 'bsnacks000@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<3.10',
}


setup(**setup_kwargs)
