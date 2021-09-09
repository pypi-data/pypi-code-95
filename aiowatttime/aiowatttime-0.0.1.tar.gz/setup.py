# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aiowatttime']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.7.4,<4.0.0']

setup_kwargs = {
    'name': 'aiowatttime',
    'version': '0.0.1',
    'description': 'An asyncio-based Python3 library for interacting with WattTime',
    'long_description': '# 🌎 aiowatttime: an asyncio-based, Python3 library for LOOK.in devices\n\n[![CI](https://github.com/bachya/aiowatttime/workflows/CI/badge.svg)](https://github.com/bachya/aiowatttime/actions)\n[![PyPi](https://img.shields.io/pypi/v/aiowatttime.svg)](https://pypi.python.org/pypi/aiowatttime)\n[![Version](https://img.shields.io/pypi/pyversions/aiowatttime.svg)](https://pypi.python.org/pypi/aiowatttime)\n[![License](https://img.shields.io/pypi/l/aiowatttime.svg)](https://github.com/bachya/aiowatttime/blob/master/LICENSE)\n[![Code Coverage](https://codecov.io/gh/bachya/aiowatttime/branch/master/graph/badge.svg)](https://codecov.io/gh/bachya/aiowatttime)\n[![Maintainability](https://api.codeclimate.com/v1/badges/a683f20d63d4735ceede/maintainability)](https://codeclimate.com/github/bachya/aiowatttime/maintainability)\n[![Say Thanks](https://img.shields.io/badge/SayThanks-!-1EAEDB.svg)](https://saythanks.io/to/bachya)\n\n`aiowatttime` is a Python 3, asyncio-friendly library for interacting with\n[WattTime](https://www.watttime.org) emissions data.\n\n- [Python Versions](#python-versions)\n- [Installation](#installation)\n- [Usage](#usage)\n- [Contributing](#contributing)\n\n# Python Versions\n\n`aiowatttime` is currently supported on:\n\n* Python 3.6\n* Python 3.7\n* Python 3.8\n* Python 3.9\n\n# Installation\n\n```python\npip install aiowatttime\n```\n\n# Usage\n\nComing soon!\n\n# Contributing\n\n1. [Check for open features/bugs](https://github.com/bachya/aiowatttime/issues)\n  or [initiate a discussion on one](https://github.com/bachya/aiowatttime/issues/new).\n2. [Fork the repository](https://github.com/bachya/aiowatttime/fork).\n3. (_optional, but highly recommended_) Create a virtual environment: `python3 -m venv .venv`\n4. (_optional, but highly recommended_) Enter the virtual environment: `source ./venv/bin/activate`\n5. Install the dev environment: `script/setup`\n6. Code your new feature or bug fix.\n7. Write tests that cover your new functionality.\n8. Run tests and ensure 100% code coverage: `script/test`\n9. Update `README.md` with any new documentation.\n10. Add yourself to `AUTHORS.md`.\n11. Submit a pull request!\n',
    'author': 'Aaron Bach',
    'author_email': 'bachya1208@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/bachya/aiowatttime',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.0,<4.0.0',
}


setup(**setup_kwargs)
