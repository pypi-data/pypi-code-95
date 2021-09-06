# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fastapi_datatables']

package_data = \
{'': ['*']}

install_requires = \
['SQLAlchemy==1.3.23',
 'fastapi>=0.68.0,<0.69.0',
 'sqlalchemy-filters>=0.12.0,<0.13.0']

setup_kwargs = {
    'name': 'fastapi-datatables',
    'version': '0.6.1',
    'description': 'A library, that makes using SQLAlchemy tables with FastAPI easy. It implements filtration, pagination, ordering and text search out of the box. With utilization of FastAPI\'s "Depends" makes it easy to get filtration data from query parameters.',
    'long_description': None,
    'author': 'LeaveMyYard',
    'author_email': 'zhukovpavel2001@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
