# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['slacktoken', 'slacktoken.commands']

package_data = \
{'': ['*']}

install_requires = \
['importlib-metadata', 'requests', 'versio']

entry_points = \
{'console_scripts': ['slacktoken = slacktoken.__main__:main']}

setup_kwargs = {
    'name': 'slacktoken',
    'version': '0.0.4',
    'description': 'A library for retrieving a Slack user token from an authenticated Slack application.',
    'long_description': None,
    'author': 'Chris Gavin',
    'author_email': 'chris@chrisgavin.me',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/chrisgavin/slacktoken/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
