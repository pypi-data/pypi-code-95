# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gaia_sdk',
 'gaia_sdk.api',
 'gaia_sdk.api.data',
 'gaia_sdk.api.transporter',
 'gaia_sdk.graphql',
 'gaia_sdk.tests']

package_data = \
{'': ['*'],
 'gaia_sdk': ['http/*', 'http/request/*', 'http/response/*', 'http/tests/*'],
 'gaia_sdk.api': ['rx/*'],
 'gaia_sdk.graphql': ['request/enumeration/*',
                      'request/input/*',
                      'request/intf/*',
                      'request/type/*',
                      'response/intf/*',
                      'response/type/*']}

install_requires = \
['Rx>=3.1.1,<4.0.0', 'requests>=2.23.0,<3.0.0']

entry_points = \
{'console_scripts': ['build = poetry_scripts:build',
                     'clean = poetry_scripts:clean',
                     'install = poetry_scripts:install',
                     'publish = poetry_scripts:publish',
                     'test = poetry_scripts:test']}

setup_kwargs = {
    'name': 'gaia-sdk',
    'version': '4.0.0rc6',
    'description': 'Python SDK for the GAIA ecosystem.',
    'long_description': None,
    'author': 'Leftshift One',
    'author_email': 'contact@leftshift.one',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
