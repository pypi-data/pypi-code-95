# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cats',
 'cats.test_utils',
 'cats.test_utils.client',
 'cats.test_utils.pytest',
 'cats.v2',
 'cats.v2.client',
 'cats.v2.server']

package_data = \
{'': ['*']}

install_requires = \
['pytz>=2021.1,<2022.0',
 'sentry-sdk>=1.3.1,<2.0.0',
 'struct-model-python>=0.1.0,<0.2.0',
 'tornado>=6.1,<7.0',
 'ujson>=4.1.0,<5.0.0']

extras_require = \
{'django': ['Django>=2.0,<3.0', 'djangorestframework>=3.12.4'],
 'djantic': ['Django>=2.0,<3.0', 'pydantic>=1.8.2', 'djantic>=0.3.3'],
 'pydantic': ['pydantic>=1.8.2']}

entry_points = \
{'pytest11': ['pytest_cats = cats.test_utils.pytest.plugin']}

setup_kwargs = {
    'name': 'cats-python',
    'version': '4.3.2',
    'description': 'Cifrazia Action Transport System for Python',
    'long_description': '# Welcome\n\n## Cifrazia Action Transport System\n\nCATS - is a TCP based byte protocol for persistence package exchanging. This so-called protocol is designed specifically\nfor internal use in [Cifrazia](https://cifrazia.com).\n\n[Learn more about protocol](./protocol)\n\n## Features\n\n+ One action at a time\n+ Up-to 4GB payload in single [plain Action](protocol/2.0.md#0x00-action)\n+ Unlimited and delayed payload in [Streaming Actions](protocol/2.0.md#0x01-streamaction)\n+ Chained [inputs](protocol/2.0.md#inputs)\n+ [Broadcasts](protocol/2.0.md#broadcast)\n+ Multiple [data formats](protocol/2.0.md#data-types)\n+ Custom [handshakes](protocol/2.0.md#handshake)\n+ ~~Local and global encryption~~\n\n[!ref](get-started.md)\n\n## Requirements\n\n+ Python `^3.9`\n+ Tornado `^6.1`\n+ Sentry SDK `^1.1.0`\n+ uJSON `^4.0.2`\n+ PyTZ `^2021.1`',
    'author': 'Bogdan Parfenov',
    'author_email': 'adam.brian.bright@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://adambrianbright.github.io/cats-python/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.10.0rc1,<4.0',
}


setup(**setup_kwargs)
