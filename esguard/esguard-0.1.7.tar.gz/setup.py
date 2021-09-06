# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['esguard']

package_data = \
{'': ['*']}

install_requires = \
['docker>=5.0.0,<6.0.0',
 'elasticsearch>=7.12.1,<8.0.0',
 'six>=1.16.0,<2.0.0',
 'tenacity>=8.0.1,<9.0.0']

setup_kwargs = {
    'name': 'esguard',
    'version': '0.1.7',
    'description': 'esguard provides a Python decorator that waits for processing while monitoring the load of Elasticsearch.',
    'long_description': '<p align="center">\n  <img alt="esguard-logo" src="esguard.png" height="100" />\n  <h2 align="center">esguard</h2>\n  <p align="center">esguard provides a Python decorator that waits for processing while monitoring the load of Elasticsearch.</p>\n</p>\n\n[![PyPi version](https://img.shields.io/pypi/v/esguard.svg)](https://pypi.python.org/pypi/esguard/) [![](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/release/python-390/) ![PyTest](https://github.com/po3rin/esguard/workflows/PyTest/badge.svg)\n\n## Quick Start\n\nYou need to launch elasticsearch before quick start.\n\n```python\nfrom esguard import ESGuard\n\n\n@ESGuard(os_cpu_percent=95).decotator\ndef mock_func(x):\n    return x\n\nself.assertEqual(mock_func(1), 1)\n```\n\n## Test\n\nYou need to launch elasticsearch before testing.\n\n```sh\n$ docker compose up -d --build\n$ poetry run pytest\n```\n',
    'author': 'po3rin',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'http://github.com/po3rin/esguard',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
