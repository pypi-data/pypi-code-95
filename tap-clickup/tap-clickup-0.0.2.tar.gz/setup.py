# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tap_clickup', 'tap_clickup.tests']

package_data = \
{'': ['*'], 'tap_clickup': ['schemas/*']}

install_requires = \
['requests>=2.25.1,<3.0.0', 'singer-sdk>=0.3.5,<0.4.0']

entry_points = \
{'console_scripts': ['tap-clickup = tap_clickup.tap:TapClickUp.cli']}

setup_kwargs = {
    'name': 'tap-clickup',
    'version': '0.0.2',
    'description': 'tap-clickup is a Singer tap for ClickUp by AutoIDM at www.autoidm.com',
    'long_description': None,
    'author': 'AutoIDM',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.1,<3.9',
}


setup(**setup_kwargs)
