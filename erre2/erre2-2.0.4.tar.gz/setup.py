# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['erre2', 'erre2.database', 'erre2.routers']

package_data = \
{'': ['*'], 'erre2': ['Files/*']}

install_requires = \
['SQLAlchemy>=1.4.19,<2.0.0',
 'aiofiles>=0.7.0,<0.8.0',
 'bcrypt>=3.2.0,<4.0.0',
 'fastapi>=0.65.2,<0.66.0',
 'passlib[bcrypt]>=1.7.4,<2.0.0',
 'psycopg2>=2.9.1,<3.0.0',
 'pytest>=6.2.5,<7.0.0',
 'python-jose[cryptography]>=3.3.0,<4.0.0',
 'python-multipart>=0.0.5,<0.0.6',
 'requests>=2.26.0,<3.0.0',
 'uvicorn[standard]>=0.14.0,<0.15.0']

setup_kwargs = {
    'name': 'erre2',
    'version': '2.0.4',
    'description': 'A new and improved version of Erre2.',
    'long_description': None,
    'author': 'Lorenzo Balugani',
    'author_email': 'lorenzo.balugani@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8.5,<4.0.0',
}


setup(**setup_kwargs)
