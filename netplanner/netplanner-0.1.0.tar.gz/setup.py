# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['netplanner',
 'netplanner.interfaces',
 'netplanner.interfaces.l2',
 'netplanner.interfaces.l3',
 'netplanner.providers',
 'netplanner.providers.networkd',
 'netplanner.providers.networkd.files',
 'netplanner.providers.networkd.templates',
 'netplanner.providers.networkd.templates.netdev_includes',
 'netplanner.providers.networkd.templates.network_includes',
 'netplanner.sriov',
 'netplanner.sriov.files']

package_data = \
{'': ['*']}

install_requires = \
['Jinja2>=3.0.1,<4.0.0',
 'PyYAML>=5.4.1,<6.0.0',
 'dacite>=1.6.0,<2.0.0',
 'fqdn>=1.5.1,<2.0.0']

entry_points = \
{'console_scripts': ['netplanner = netplanner.__main__:main']}

setup_kwargs = {
    'name': 'netplanner',
    'version': '0.1.0',
    'description': '"Mimir the Netplanner is the ground of all network wisdöm"',
    'long_description': None,
    'author': 'Marcel Fest',
    'author_email': 'marcel.fest@telekom.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
