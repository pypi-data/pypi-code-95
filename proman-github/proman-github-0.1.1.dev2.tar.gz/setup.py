# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['proman_github']

package_data = \
{'': ['*']}

install_requires = \
['PyGithub>=1.55,<2.0',
 'argufy>=0.1.2-alpha.1,<0.2.0',
 'proman-common>=0.1.1-alpha.1,<0.2.0',
 'python-magic>=0.4.24,<0.5.0']

entry_points = \
{'console_scripts': ['gh = proman_github:__main__.main',
                     'github = proman_github:__main__.main']}

setup_kwargs = {
    'name': 'proman-github',
    'version': '0.1.1.dev2',
    'description': 'GitHub based package manager.',
    'long_description': None,
    'author': 'Jesse P. Johnson',
    'author_email': 'jpj6652@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
