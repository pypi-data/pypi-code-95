# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gaea',
 'gaea.config',
 'gaea.constants',
 'gaea.database',
 'gaea.database.utils',
 'gaea.errors',
 'gaea.helpers',
 'gaea.log',
 'gaea.models',
 'gaea.models.utils',
 'gaea.rbmq',
 'gaea.rbmq.utils',
 'gaea.redis',
 'gaea.webapp']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.7.4,<4.0.0',
 'alembic>=1,<2',
 'dynaconf>=3,<4',
 'fastapi>=0,<1',
 'pika>=1,<2',
 'psycopg2-binary>=2,<3',
 'pydantic>=1,<2',
 'redis>=3,<4',
 'sqlalchemy>=1,<2',
 'uvicorn>=0,<1']

setup_kwargs = {
    'name': 'gaea',
    'version': '1.8.2',
    'description': 'A microservice chassis for akingbee.com !',
    'long_description': None,
    'author': 'rarnal',
    'author_email': 'arnal.romain@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
