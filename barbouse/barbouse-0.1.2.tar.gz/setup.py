# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['barbouse']

package_data = \
{'': ['*']}

install_requires = \
['Pygments>=2.9.0,<3.0.0', 'jq>=1.1.3,<2.0.0', 'requests>=2.25.1,<3.0.0']

entry_points = \
{'console_scripts': ['barbouse = barbouse.barbouse:main']}

setup_kwargs = {
    'name': 'barbouse',
    'version': '0.1.2',
    'description': 'Postman for bearded API users',
    'long_description': None,
    'author': 'Guillaume Pasquet',
    'author_email': 'dev@etenil.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
