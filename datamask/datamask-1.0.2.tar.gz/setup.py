# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['datamask']

package_data = \
{'': ['*']}

install_requires = \
['Faker>=8.12.1,<9.0.0',
 'psycopg2-binary>2.8.0,<2.10',
 'python-slugify>4.0.0,<6.0.0']

entry_points = \
{'console_scripts': ['datadict = datamask.datadict:main',
                     'datamask = datamask.cleaner:main']}

setup_kwargs = {
    'name': 'datamask',
    'version': '1.0.2',
    'description': 'Data PII cleaning/masking for databases',
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
