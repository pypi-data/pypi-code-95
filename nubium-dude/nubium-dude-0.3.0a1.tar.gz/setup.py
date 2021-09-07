# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': '.'}

packages = \
['dude', 'dude._commands', 'dude.api']

package_data = \
{'': ['*']}

install_requires = \
['black>=21.6b0,<22.0',
 'click>=8.0.1,<9.0.0',
 'confluent-kafka[avro]>=1.7.0,<2.0.0',
 'nubium-schemas>=1.1.1,<2.0.0',
 'virtualenv-api>=2.1.18,<3.0.0',
 'virtualenv>=20.4.7,<21.0.0']

entry_points = \
{'console_scripts': ['dude = dude.__main__:main']}

setup_kwargs = {
    'name': 'nubium-dude',
    'version': '0.3.0a1',
    'description': 'CLI tool for automating various development tasks',
    'long_description': None,
    'author': 'RedHat Marketing Operations Data Engineering',
    'author_email': 'mkt-ops-de@redhat.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
