# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pgdatacleaner']

package_data = \
{'': ['*']}

install_requires = \
['Faker>=8.12.1,<9.0.0',
 'psycopg2-binary>=2.9.1,<3.0.0',
 'python-slugify>=5.0.2,<6.0.0']

entry_points = \
{'console_scripts': ['dataclean = pgdatacleaner.cleaner:main',
                     'datadict = pgdatacleaner.datadict:main']}

setup_kwargs = {
    'name': 'pgdatacleaner',
    'version': '1.1.0a6',
    'description': 'Data cleaning/masking for PostgreSQL databases',
    'long_description': None,
    'author': 'Fredrik Håård',
    'author_email': 'fredrik@metallapan.se',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4',
}


setup(**setup_kwargs)
