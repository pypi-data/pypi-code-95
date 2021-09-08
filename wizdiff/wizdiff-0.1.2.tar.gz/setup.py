# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['wizdiff']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.1,<9.0.0', 'loguru>=0.5.3,<0.6.0', 'requests>=2.26.0,<3.0.0']

entry_points = \
{'console_scripts': ['wizdiff = wizdiff.__main__:main']}

setup_kwargs = {
    'name': 'wizdiff',
    'version': '0.1.2',
    'description': '',
    'long_description': None,
    'author': 'StarrFox',
    'author_email': 'starrfox6312@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
