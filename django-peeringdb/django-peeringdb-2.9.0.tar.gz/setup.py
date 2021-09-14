# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['django_peeringdb',
 'django_peeringdb.admin',
 'django_peeringdb.client_adaptor',
 'django_peeringdb.management',
 'django_peeringdb.management.commands',
 'django_peeringdb.migrations',
 'django_peeringdb.models']

package_data = \
{'': ['*']}

install_requires = \
['django_countries>1', 'django_handleref>=1,<2', 'django_inet>=1,<2']

entry_points = \
{'markdown.extensions': ['pymdgen = pymdgen.md:Extension']}

setup_kwargs = {
    'name': 'django-peeringdb',
    'version': '2.9.0',
    'description': 'PeeringDB Django models',
    'long_description': '\n# django-peeringdb\n\n[![PyPI](https://img.shields.io/pypi/v/django_peeringdb.svg?maxAge=2592000)](https://pypi.python.org/pypi/django_peeringdb)\n[![PyPI](https://img.shields.io/pypi/pyversions/django-peeringdb.svg)](https://pypi.python.org/pypi/django-peeringdb)\n[![Tests](https://github.com/peeringdb/django-peeringdb/workflows/tests/badge.svg)](https://github.com/peeringdb/django-peeringdb)\n[![LGTM Grade](https://img.shields.io/lgtm/grade/python/github/20c/django-peeringdb)](https://lgtm.com/projects/g/20c/django-peeringdb/alerts/)\n[![Codecov](https://img.shields.io/codecov/c/github/peeringdb/django-peeringdb/master.svg?maxAge=2592000)](https://codecov.io/github/peeringdb/django-peeringdb)\n\nDjango models for PeeringDB\n\nSee the docs at http://peeringdb.github.io/django-peeringdb/\n\n',
    'author': 'PeeringDB',
    'author_email': 'support@peeringdb.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/peeringdb/django-peeringdb',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
