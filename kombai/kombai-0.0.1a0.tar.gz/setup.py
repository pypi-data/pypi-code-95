# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['kombai']

package_data = \
{'': ['*']}

install_requires = \
['SQLAlchemy>=1.4,<1.4.23',
 'pytest-cov>=2.12.1,<3.0.0',
 'textual>=0.1.10,<0.2.0']

extras_require = \
{':python_version < "3.8"': ['importlib-metadata>=4.8.1,<5.0.0']}

setup_kwargs = {
    'name': 'kombai',
    'version': '0.0.1a0',
    'description': 'Terminal based structured data viewer and editor written in Python',
    'long_description': '[![PyPI Version](https://img.shields.io/pypi/v/kombai)](https://pypi.org/project/kombai/)\n[![Python Versions](https://img.shields.io/pypi/pyversions/kombai)](https://pypi.org/project/kombai/)\n[![Python Wheel](https://img.shields.io/pypi/wheel/kombai)](https://pypi.org/project/kombai/)\n[![License](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)\n[![Code Style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![Code Quality: flake8](https://img.shields.io/badge/code%20quality-flake8-000000.svg)](https://gitlab.com/pycqa/flake8)\n\n# kombai\nTerminal based structured data viewer and editor written in Python\n\n## Contributing\nPlease refer to [CONTRIBUTING.md](CONTRIBUTING.md) file for more information on how to\ncontribute to this project.\n',
    'author': 'kracekumar',
    'author_email': 'me@kracekumar.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
