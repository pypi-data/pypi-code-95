# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['suade_reverse_repo',
 'suade_reverse_repo.core',
 'suade_reverse_repo.core.repo',
 'suade_reverse_repo.core.security',
 'suade_reverse_repo.data',
 'suade_reverse_repo.models']

package_data = \
{'': ['*']}

install_requires = \
['atomicwrites==1.4.0',
 'attrs==21.2.0',
 'colorama==0.4.4',
 'iniconfig==1.1.1',
 'numpy==1.21.2',
 'packaging==21.0',
 'pandas>=1.3.3,<2.0.0',
 'pluggy==1.0.0',
 'py==1.10.0',
 'pydantic>=1.8.2,<2.0.0',
 'pyparsing==2.4.7',
 'pytest>=6.2.5,<7.0.0',
 'pytz==2021.1',
 'six==1.16.0',
 'toml==0.10.2',
 'typing-extensions>=3.10.0,<4.0.0']

setup_kwargs = {
    'name': 'suade-reverse-repo',
    'version': '0.1.4',
    'description': 'This package includes classes to model reverse repo transactions and calculate the associated ktcd factor.',
    'long_description': None,
    'author': 'Moe Bourji',
    'author_email': 'mrbourji@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.9',
}


setup(**setup_kwargs)
