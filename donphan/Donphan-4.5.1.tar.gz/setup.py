# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['donphan']

package_data = \
{'': ['*']}

modules = \
['py']
install_requires = \
['asyncpg>=0.22.0']

extras_require = \
{'docs': ['sphinx>=3.5.3',
          'sphinxcontrib_trio>=1.1.2',
          'sphinxcontrib-websupport>=1.2.4']}

setup_kwargs = {
    'name': 'donphan',
    'version': '4.5.1',
    'description': 'Asynchronous Database ORM for Postgres',
    'long_description': 'Donphan\n=======\n\n.. image:: https://readthedocs.org/projects/donphan/badge/?version=latest\n    :target: https://donphan.readthedocs.io/en/latest/?badge=latest\n    :alt: Documentation Status\n\nAsynchronous database ORM for use with Postgres.',
    'author': 'bijij',
    'author_email': 'josh@josh-is.gay',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'py_modules': modules,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
