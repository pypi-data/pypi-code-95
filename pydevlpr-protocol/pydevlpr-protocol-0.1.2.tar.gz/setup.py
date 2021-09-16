# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['pydevlpr_protocol']

package_data = \
{'': ['*']}

install_requires = \
['mypy>=0.910,<0.911']

setup_kwargs = {
    'name': 'pydevlpr-protocol',
    'version': '0.1.2',
    'description': 'The protocol used by the DELVPR Daemon to transfer data',
    'long_description': '# PyDEVLPR-Protocol\n\nThis is the shared protocol used between the devlprd and pydevlpr. They communicate over a socket that formats messages very particularly.',
    'author': 'Ezra Boley',
    'author_email': 'hello@getfantm.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
