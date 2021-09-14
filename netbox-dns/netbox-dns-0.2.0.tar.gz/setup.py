# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['netbox_dns',
 'netbox_dns.api',
 'netbox_dns.core',
 'netbox_dns.migrations',
 'netbox_dns.templatetags']

package_data = \
{'': ['*'], 'netbox_dns': ['templates/netbox_dns/*']}

setup_kwargs = {
    'name': 'netbox-dns',
    'version': '0.2.0',
    'description': 'Netbox Dns is a netbox plugin for managing zone, nameserver and record inventory.',
    'long_description': '<h1 align="center">Netbox DNS</h1>\n\n<p align="center"><i>Netbox Dns is a netbox plugin for managing zone, nameserver and record inventory.</i></p>\n\n<div align="center">\n<a href="https://github.com/auroraresearchlab/netbox-dns/stargazers"><img src="https://img.shields.io/github/stars/auroraresearchlab/netbox-dns" alt="Stars Badge"/></a>\n<a href="https://github.com/auroraresearchlab/netbox-dns/network/members"><img src="https://img.shields.io/github/forks/auroraresearchlab/netbox-dns" alt="Forks Badge"/></a>\n<a href="https://github.com/auroraresearchlab/netbox-dns/pulls"><img src="https://img.shields.io/github/issues-pr/auroraresearchlab/netbox-dns" alt="Pull Requests Badge"/></a>\n<a href="https://github.com/auroraresearchlab/netbox-dns/issues"><img src="https://img.shields.io/github/issues/auroraresearchlab/netbox-dns" alt="Issues Badge"/></a>\n<a href="https://github.com/auroraresearchlab/netbox-dns/graphs/contributors"><img alt="GitHub contributors" src="https://img.shields.io/github/contributors/auroraresearchlab/netbox-dns?color=2b9348"></a>\n<a href="https://github.com/auroraresearchlab/netbox-dns/blob/master/LICENSE"><img src="https://img.shields.io/github/license/auroraresearchlab/netbox-dns?color=2b9348" alt="License Badge"/></a>\n</div>\n\n## Features\n\n* Manage zones (domains) you have.\n* Manage nameservers for zones.\n* Manage zone records.\n* Assign tags to zones, nameservers and records.\n\n## Requirements\n\n* Netbox 3.0\n* python 3.7\n\n## Installation\n\n```\n$ pip install netbox-dns\n```\n\n## Screenshots\n\n![Zones](media/zones.png)\n\n![Zone Detail](media/zone-detail.png)\n\n## Contribute\n\nContributions are always welcome!\n\n## License\n\nMIT\n',
    'author': 'Aurora Research Lab',
    'author_email': 'info@auroraresearchlab.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/auroraresearchlab/netbox-dns',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
