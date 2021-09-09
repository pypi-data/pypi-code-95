# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['kw6']

package_data = \
{'': ['*']}

install_requires = \
['Pillow>=8.3.1,<9.0.0', 'numpy>=1.21.2,<2.0.0', 'pydantic>=1.8.2,<2.0.0']

setup_kwargs = {
    'name': 'kw6',
    'version': '0.2.6',
    'description': 'Minimalistic library for reading files in the kw6 file format',
    'long_description': None,
    'author': 'Aiwizo AB',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
