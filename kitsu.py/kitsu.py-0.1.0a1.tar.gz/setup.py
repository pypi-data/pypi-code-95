# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['kitsu']

package_data = \
{'': ['*']}

modules = \
['LICENSE']
install_requires = \
['aiohttp>=3.7.4,<4.0.0', 'python-dateutil>=2.8.2,<3.0.0']

setup_kwargs = {
    'name': 'kitsu.py',
    'version': '0.1.0a1',
    'description': 'A simple asynchronous python wrapper for the kitsu.io API',
    'long_description': '<div align="center">\n  <h1>Kitsu.py</h1>\n  <a href="https://github.com/MrArkon/kitsu.py/graphs/contributors">\n    <img src="https://img.shields.io/github/contributors/MrArkon/kitsu.py.svg?style=for-the-badge" />\n  </a>\n  <a href="https://github.com/MrArkon/kitsu.py/network/members">\n    <img src="https://img.shields.io/github/forks/MrArkon/kitsu.py.svg?style=for-the-badge" />\n  </a>\n  <a href="https://github.com/MrArkon/kitsu.py/stargazers">\n    <img src="https://img.shields.io/github/stars/MrArkon/kitsu.py.svg?style=for-the-badge" />\n  </a>\n  <a href="https://github.com/MrArkon/kitsu.py/issues">\n    <img src="https://img.shields.io/github/issues/MrArkon/kitsu.py.svg?style=for-the-badge" />\n  </a>\n  <a href="https://github.com/MrArkon/kitsu.py/blob/master/LICENSE.txt">\n    <img src="https://img.shields.io/github/license/MrArkon/kitsu.py.svg?style=for-the-badge" />\n  </a>\n  </div>\n  <p align="center">\n    A simple & lightweight JSON client for the <a href="https://kitsu.io/">Kitsu.io</a> API\n    <br />\n    <br />\n    <a href="https://pypi.org/project/kitsu.py/">PyPi</a>\n    ·\n    <a href="https://github.com/MrArkon/kitsu.py/issues">Report Bugs</a>\n    ·\n    <a href="https://github.com/MrArkon/kitsu.py/issues">Request Feature</a>\n  </p>\n</p>\n\n## License\n\nThis project is distributed under the MIT license.\n',
    'author': 'MrArkon',
    'author_email': None,
    'maintainer': 'MrArkon',
    'maintainer_email': None,
    'url': 'https://github.com/MrArkon/kitsu.py/',
    'packages': packages,
    'package_data': package_data,
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
