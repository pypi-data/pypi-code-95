# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyelexon']

package_data = \
{'': ['*']}

install_requires = \
['requests==2.25.1']

setup_kwargs = {
    'name': 'pyelexon',
    'version': '0.1.1',
    'description': '',
    'long_description': '# pyelexon\n\nSimple python wrapper for the Elexon BMRS API.\n\n[![](https://img.shields.io/badge/python-3.8-blue.svg)](https://github.com/pyenv/pyenv)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)\n\n## Getting started\n\n* Register on the Elexon BMRS [data portal](https://www.elexonportal.co.uk/news/latest?cachebust=q3pzb5uiac)\nand retrieve your `api_key`\n\n* Example usage\n```python\nfrom datetime import date\nfrom pyelexon import Elexon\n\napi_key = "123456"\nreport = "DETSYSPRICES"\nsettlement_date = date(2021, 9, 15)\nsettlement_period = 1\n\nelexon = Elexon(api_key)\n# returns content of response\nr: bytes = elexon.fetch_settlement(report, settlement_date, settlement_period)\n```\n\n## Tested reports\n\n* `DETSYSPRICES`\n* `PHYBMDATA`\n* `DYNBMDATA`\n',
    'author': 'atsangarides',
    'author_email': 'andreas_tsangarides@hotmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/atsangarides/pyelexon',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
