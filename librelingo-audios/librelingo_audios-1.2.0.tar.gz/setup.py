# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['librelingo_audios']

package_data = \
{'': ['*']}

install_requires = \
['librelingo-utils>=2.4.0,<3.0.0', 'librelingo-yaml-loader>=1.5.0,<2.0.0']

setup_kwargs = {
    'name': 'librelingo-audios',
    'version': '1.2.0',
    'description': 'Tools to help getting audios for LibreLingo courses',
    'long_description': None,
    'author': 'Dániel Kántor',
    'author_email': 'git@daniel-kantor.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
