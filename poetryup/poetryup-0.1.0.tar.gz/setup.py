# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['poetryup']

package_data = \
{'': ['*']}

install_requires = \
['toml>=0.10.2,<0.11.0']

entry_points = \
{'console_scripts': ['poetryup = poetryup.poetryup:poetryup']}

setup_kwargs = {
    'name': 'poetryup',
    'version': '0.1.0',
    'description': 'Run poetry update and bump versions in pyproject.toml file',
    'long_description': 'None',
    'author': 'Mousa Zeid Baker',
    'author_email': 'None',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
