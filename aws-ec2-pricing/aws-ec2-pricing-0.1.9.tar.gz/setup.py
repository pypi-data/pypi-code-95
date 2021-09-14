# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ec2pricing']

package_data = \
{'': ['*']}

install_requires = \
['boto3>=1.18.40,<2.0.0', 'click>=8.0.1,<9.0.0', 'prettytable>=2.2.0,<3.0.0']

entry_points = \
{'console_scripts': ['ec2pricing = ec2pricing:cli']}

setup_kwargs = {
    'name': 'aws-ec2-pricing',
    'version': '0.1.9',
    'description': 'CLI tool to build SQLite table from AWS EC2 prices.',
    'long_description': None,
    'author': 'vduseev',
    'author_email': 'vagiz@duseev.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
