# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['arkive', 'arkive.actions', 'arkive.core', 'arkive.drives', 'arkive.utility']

package_data = \
{'': ['*']}

install_requires = \
['beautifultable>=1.0.1,<2.0.0',
 'pathvalidate>=2.3.2,<3.0.0',
 'tinytag>=1.5.0,<2.0.0',
 'wcwidth>=0.2.5,<0.3.0']

entry_points = \
{'console_scripts': ['arkive = arkive.__main__:main']}

setup_kwargs = {
    'name': 'arkive',
    'version': '0.2.3',
    'description': 'Manage your music/audio collections.',
    'long_description': None,
    'author': 'Orlando Ospino Sánchez',
    'author_email': 'oroschz@outlook.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/oroschz/arkive',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
