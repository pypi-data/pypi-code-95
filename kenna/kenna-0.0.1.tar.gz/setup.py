# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['kenna',
 'kenna.cli',
 'kenna.cli.command_groups',
 'kenna.data',
 'kenna.data.constants',
 'kenna.data.types']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.0,<8.0', 'hodgepodge>=0.1.7,<0.2.0']

entry_points = \
{'console_scripts': ['kenna = kenna.cli:cli']}

setup_kwargs = {
    'name': 'kenna',
    'version': '0.0.1',
    'description': '',
    'long_description': '# Kenna\n\n> An API client for Kenna Security\n\n![Kenna](https://raw.githubusercontent.com/whitfieldsdad/images/main/kenna-hero.png)\n\n## Installation\n\nTo install from source:\n\n```shell\n$ git clone git@github.com:whitfieldsdad/python-kenna-api-client.git\n$ make install\n```\n\n## Tutorials\n\nThe following general options are available:\n\n```shell\n$ poetry run kenna\nUsage: kenna [OPTIONS] COMMAND [ARGS]...\n\nOptions:\n  --api-key TEXT\n  --region TEXT\n  --help          Show this message and exit.\n\nCommands:\n  applications\n  assets\n  connectors\n  dashboard-groups\n  fixes\n  roles\n  users\n  vulnerabilities\n```\n\n### Applications\n\nThe following options are available when listing applications.\n\n```shell\n$ poetry run kenna applications\nUsage: kenna applications [OPTIONS] COMMAND [ARGS]...\n\nOptions:\n  --help  Show this message and exit.\n\nCommands:\n  count-applications\n  get-application\n  get-application-ids\n  get-application-names\n  get-application-owners\n  get-applications\n```\n\n### Assets\n\nThe following options are available when listing assets: \n\n```shell\n$ poetry run kenna assets\nUsage: kenna assets [OPTIONS] COMMAND [ARGS]...\n\nOptions:\n  --help  Show this message and exit.\n\nCommands:\n  count-assets\n  get-asset\n  get-asset-hostnames\n  get-asset-ipv4-addresses\n  get-asset-ipv6-addresses\n  get-asset-tags\n  get-assets\n```\n\n### Connectors\n\nThe following options are available when listing connectors:\n\n```shell\n$ poetry run kenna connectors\nUsage: kenna connectors [OPTIONS] COMMAND [ARGS]...\n\nOptions:\n  --help  Show this message and exit.\n\nCommands:\n  count-connectors\n  get-connector\n  get-connector-run\n  get-connector-runs\n  get-connectors\n```\n\n### Dashboard groups\n\nThe following options are available when listing dashboard groups:\n\n```shell\n$ poetry run kenna dashboard-groups\nUsage: kenna dashboard-groups [OPTIONS] COMMAND [ARGS]...\n\nOptions:\n  --help  Show this message and exit.\n\nCommands:\n  count-dashboard-groups\n  get-dashboard-group\n  get-dashboard-groups\n```\n\n### Fixes\n\nThe following options are available when listing fixes:\n\n```shell\n$ poetry run kenna fixes\nUsage: kenna fixes [OPTIONS] COMMAND [ARGS]...\n\nOptions:\n  --help  Show this message and exit.\n\nCommands:\n  count-fixes\n  get-fix\n  get-fixes\n```\n\n### Users\n\nThe following options are available when listing users:\n\n```shell\n$ poetry run kenna users\nUsage: kenna users [OPTIONS] COMMAND [ARGS]...\n\nOptions:\n  --help  Show this message and exit.\n\nCommands:\n  count-users\n  get-user\n  get-users\n```\n\n### Roles\n\nThe following options are available when listing roles:\n\n```shell\n$ poetry run kenna roles\nUsage: kenna roles [OPTIONS] COMMAND [ARGS]...\n\nOptions:\n  --help  Show this message and exit.\n\nCommands:\n  count-roles\n  get-role\n  get-roles\n```\n\n### Vulnerabilities\n\nThe following options are available when listing vulnerabilities:\n\n```shell\n$ poetry run kenna vulnerabilities\nUsage: kenna vulnerabilities [OPTIONS] COMMAND [ARGS]...\n\nOptions:\n  --help  Show this message and exit.\n\nCommands:\n  count-vulnerabilities\n  get-vulnerabilities\n  get-vulnerability\n```\n',
    'author': 'Tyler Fisher',
    'author_email': 'tylerfisher@tylerfisher.ca',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.0,<4',
}


setup(**setup_kwargs)
