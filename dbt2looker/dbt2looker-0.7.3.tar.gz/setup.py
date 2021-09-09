# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dbt2looker', 'dbt2looker.dbt_json_schemas']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=5.4.1,<6.0.0',
 'importlib-metadata>=4.8.1,<5.0.0',
 'jsonschema>=3.2.0,<4.0.0',
 'lkml>=1.1.0,<2.0.0',
 'pydantic>=1.8.1,<2.0.0',
 'typing-extensions>=3.10.0,<4.0.0']

entry_points = \
{'console_scripts': ['dbt2looker = dbt2looker.cli:run']}

setup_kwargs = {
    'name': 'dbt2looker',
    'version': '0.7.3',
    'description': 'Generate lookml view files from dbt models',
    'long_description': '# dbt2looker\n\nUse `dbt2looker` to generate Looker view files automatically from dbt models.\n\nWant a deeper integration between dbt and your BI tool? You should also checkout [Lightdash - the open source alternative to Looker](https://github.com/lightdash/lightdash)\n\n**Features**\n\n* **Column descriptions** synced to looker\n* **Dimension** for each column in dbt model\n* **Dimension groups** for datetime/timestamp/date columns\n* **Measures** defined through dbt column `metadata` [see below](#defining-measures)\n* Looker types\n* Warehouses: BigQuery, Snowflake, Redshift (postgres to come)\n\n[![demo](https://raw.githubusercontent.com/hubble-data/dbt2looker/main/docs/demo.gif)](https://asciinema.org/a/407407)\n\n## Quickstart\n\nRun `dbt2looker` in the root of your dbt project *after compiling looker docs*.\n\n**Generate Looker view files for all models:**\n```shell\ndbt docs generate\ndbt2looker\n```\n\n**Generate Looker view files for all models tagged `prod`**\n```shell\ndbt2looker --tag prod\n```\n\n## Install\n\n**Install from PyPi repository**\n\nInstall from pypi into a fresh virtual environment.\n\n```\n# Create virtual env\npython3.7 -m venv dbt2looker-venv\nsource dbt2looker-venv/bin/activate\n\n# Install\npip install dbt2looker\n\n# Run\ndbt2looker\n```\n\n**Build from source**\n\nRequires [poetry](https://python-poetry.org/docs/) and python >=3.7\n\nFor development, it is recommended to use python 3.7:\n\n```\n# Ensure you\'re using 3.7\npoetry env use 3.7  \n# alternative: poetry env use /usr/local/opt/python@3.7/bin/python3\n\n# Install dependencies and main package\npoetry install\n\n# Run dbtlooker in poetry environment\npoetry run dbt2looker\n```\n\n## Defining measures\n\nYou can define looker measures in your dbt `schema.yml` files. For example:\n\n```yaml\nmodels:\n  - name: pages\n    columns:\n      - name: url\n        description: "Page url"\n      - name: event_id\n        description: unique event id for page view\n        meta:\n           measures:\n             page_views:\n               type: count\n```\n',
    'author': 'oliverlaslett',
    'author_email': 'oliver@gethubble.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/hubble-data/dbt2looker',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7',
}


setup(**setup_kwargs)
