# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mouser']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0,<9.0', 'requests>=2.26,<3.0']

entry_points = \
{'console_scripts': ['mouser = mouser.cli:mouser_cli']}

setup_kwargs = {
    'name': 'mouser',
    'version': '0.1.1',
    'description': 'Mouser Python API',
    'long_description': "# Mouser Python API\n\n[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](https://github.com/sparkmicro/mouser-api/blob/main/LICENSE)\n[![Python Versions](https://raw.githubusercontent.com/sparkmicro/Ki-nTree/master/images/python_versions.svg)](https://www.python.org/)\n[![PyPI](https://img.shields.io/pypi/v/mouser)](https://pypi.org/project/mouser/)\n[![Style | Tests](https://github.com/sparkmicro/mouser-api/actions/workflows/tests.yaml/badge.svg)](https://github.com/sparkmicro/mouser-api/actions)\n\n## Setup\n\n### Requirements\n\n* Tested with Python 3.7+\n* Dependencies: [click](https://click.palletsprojects.com/en/8.0.x/) and [requests](https://docs.python-requests.org/en/master/) packages\n\n### Mouser API Keys\n\nMouser provides two separate API keys:\n* one for the cart and orders\n* one for part searches.\n\nGo to [Mouser's API hub](https://www.mouser.com/api-hub/) to request the keys.\n\nTo store the keys, two options:\n* create two environmental variables `MOUSER_ORDER_API_KEY` and `MOUSER_PART_API_KEY` with the respective values of each key\n* create a file named `mouser_api_keys.yaml` with the order API key on the first line and the part API key on a second line.\n\nThe keys will be automatically loaded for each API request.\n\n### Install\n\n#### Pip\n\n``` bash\npip install mouser\n```\n\n#### Manually\n\n1. Create virtual environment and activate it\n2. Run `pip install -r requirements.txt`\n\n#### Poetry\n\n1. Install `poetry` package: `pip install poetry`\n2. Run `poetry install`\n\n### Run\n\n#### Pip\n\n```bash\nmouser\n```\n\n#### Manually\n\n```bash\npython mouser_cli.py\n```\n\n#### Poetry\n\n```bash\npoetry run mouser\n```\n\n## Usage\n\nThis command line tool reflects the usage from Mouser's API structure [documented here](https://api.mouser.com/api/docs/ui/index#/).  \nThe first positional argument is the category of the request: cart (for MouserCart), order, history (for MouserOrderHistory) and search (for SearchAPI).\nThe second argument is the type of operation from the list of operations for each category.\n\nRun `mouser --help` for more information about the usage.\n\n### Examples\n> The examples below assume this package was installed using Pip (for more options, see [above](#run))\n\n#### Part Number Search\n```bash\nmouser search partnumber --number XXX\n```\n\n#### Export order to CSV\n``` bash\nmouser order get --number XXX --export\n```\n",
    'author': 'eeintech',
    'author_email': 'eeintech@eeinte.ch',
    'maintainer': 'eeintech',
    'maintainer_email': 'eeintech@eeinte.ch',
    'url': 'https://github.com/sparkmicro/mouser',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
