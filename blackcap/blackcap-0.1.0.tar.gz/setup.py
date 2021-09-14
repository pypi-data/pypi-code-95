# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['blackcap',
 'blackcap.auther',
 'blackcap.blocs',
 'blackcap.cli',
 'blackcap.configs',
 'blackcap.messenger',
 'blackcap.migrations',
 'blackcap.models',
 'blackcap.models.meta',
 'blackcap.observer',
 'blackcap.routes',
 'blackcap.routes.job',
 'blackcap.routes.schedule',
 'blackcap.routes.user',
 'blackcap.scheduler',
 'blackcap.schemas',
 'blackcap.schemas.api',
 'blackcap.schemas.api.auth',
 'blackcap.schemas.api.cluster',
 'blackcap.schemas.api.job',
 'blackcap.schemas.api.schedule',
 'blackcap.schemas.api.user',
 'blackcap.tasks',
 'blackcap.utils']

package_data = \
{'': ['*']}

install_requires = \
['Flask-Cors>=3.0.10,<4.0.0',
 'Flask>=2.0.1,<3.0.0',
 'PyJWT>=2.1.0,<3.0.0',
 'SQLAlchemy-serializer>=1.4.1,<2.0.0',
 'SQLAlchemy>=1.4.22,<2.0.0',
 'alembic>=1.6.5,<2.0.0',
 'bcrypt>=3.2.0,<4.0.0',
 'celery>=5.1.0,<6.0.0',
 'click<8.0',
 'google-cloud-pubsub>=2.5.0,<3.0.0',
 'gunicorn>=20.1.0,<21.0.0',
 'logzero>=1.7.0,<2.0.0',
 'psycopg2-binary>=2.8.6,<3.0.0',
 'pydantic[dotenv]>=1.8.2,<2.0.0',
 'redis>=3.5.3,<4.0.0',
 'xdg>=5.0.2,<6.0.0']

entry_points = \
{'console_scripts': ['blackcap = blackcap.cli.main:main']}

setup_kwargs = {
    'name': 'blackcap',
    'version': '0.1.0',
    'description': 'Shared library for Orchestra',
    'long_description': None,
    'author': 'Ankur Kumar',
    'author_email': 'ank@leoank.me',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
