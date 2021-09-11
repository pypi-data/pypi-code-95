# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['algo_method_tools']

package_data = \
{'': ['*']}

install_requires = \
['beautifulsoup4>=4.10.0,<5.0.0',
 'requests>=2.26.0,<3.0.0',
 'typer>=0.4.0,<0.5.0']

entry_points = \
{'console_scripts': ['algo-tools = algo_method_tools.main:main']}

setup_kwargs = {
    'name': 'algo-method-tools',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'yassu',
    'author_email': 'yassu0320.dev@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
