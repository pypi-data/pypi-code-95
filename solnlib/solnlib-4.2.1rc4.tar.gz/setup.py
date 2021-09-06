# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['solnlib', 'solnlib.modular_input']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.24,<3.0', 'sortedcontainers>=2.2,<3.0', 'splunk-sdk==1.6.16']

setup_kwargs = {
    'name': 'solnlib',
    'version': '4.2.1rc4',
    'description': 'The Splunk Software Development Kit for Splunk Solutions',
    'long_description': None,
    'author': 'Splunk',
    'author_email': 'addonfactory@splunk.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/splunk/addonfactory-solutions-library-python',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
