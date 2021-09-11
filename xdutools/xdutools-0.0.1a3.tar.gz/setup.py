# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['xdutools', 'xdutools.apps', 'xdutools.auth']

package_data = \
{'': ['*']}

install_requires = \
['beautifulsoup4>=4.10.0,<5.0.0',
 'httpx>=0.19.0,<0.20.0',
 'pycryptodome>=3.10.1,<4.0.0']

extras_require = \
{'all': ['asyncclick>=8.0.1.3,<9.0.0.0', 'colorama>=0.4.4,<0.5.0'],
 'cli': ['asyncclick>=8.0.1.3,<9.0.0.0']}

entry_points = \
{'console_scripts': ['xdu = xdutools.cli:main']}

setup_kwargs = {
    'name': 'xdutools',
    'version': '0.0.1a3',
    'description': '西电相关工具和 CLI',
    'long_description': 'None',
    'author': 'shoor',
    'author_email': 'shoorday@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/shoorday/xdutools',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
