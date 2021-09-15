# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dash',
 'dash.categories',
 'dash.categories.migrations',
 'dash.dashblocks',
 'dash.dashblocks.migrations',
 'dash.dashblocks.templatetags',
 'dash.orgs',
 'dash.orgs.management',
 'dash.orgs.management.commands',
 'dash.orgs.migrations',
 'dash.orgs.templatetags',
 'dash.stories',
 'dash.stories.migrations',
 'dash.tags',
 'dash.tags.migrations',
 'dash.users',
 'dash.utils',
 'dash.utils.management',
 'dash.utils.management.commands',
 'dash.utils.templatetags']

package_data = \
{'': ['*'],
 'dash.categories': ['templates/categories/*'],
 'dash.dashblocks': ['static/css/*',
                     'static/css/font/*',
                     'static/js/*',
                     'templates/dashblocks/*'],
 'dash.orgs': ['templates/*', 'templates/orgs/*', 'templates/orgs/email/*'],
 'dash.stories': ['templates/stories/*']}

install_requires = \
['Django<4.0',
 'Pillow>=8.1.0,<9.0.0',
 'celery<5.0',
 'django-compressor>=2.4,<3.0',
 'django-hamlpy>=1.4.3,<2.0.0',
 'django-redis>=4.12.1,<5.0.0',
 'django-timezone-field>=4.1.1,<5.0.0',
 'phonenumbers>=8.12.16,<9.0.0',
 'psycopg2-binary<2.9.0',
 'python-dateutil>=2.8.1,<3.0.0',
 'rapidpro-python>=2.8.3,<3.0.0',
 'smartmin>=3.0.0,<4.0.0',
 'sorl-thumbnail>=12.7.0,<13.0.0']

setup_kwargs = {
    'name': 'rapidpro-dash',
    'version': '1.7.3',
    'description': 'Support library for RapidPro dashboards',
    'long_description': None,
    'author': 'Nyaruka Ltd',
    'author_email': 'code@nyaruka.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
