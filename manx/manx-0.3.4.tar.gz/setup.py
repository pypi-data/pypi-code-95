# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['manx']

package_data = \
{'': ['*']}

install_requires = \
['elasticsearch[async]>=7.10.1,<8.0.0']

setup_kwargs = {
    'name': 'manx',
    'version': '0.3.4',
    'description': 'Data migrations for elasticsearch',
    'long_description': '# Manx: Migrations for elasticsearch\n[![coverage report](https://gitlab.com/text-analytics/open-source/manx/badges/master/coverage.svg)](https://gitlab.com/text-analytics/open-source/manx/-/commits/master)\n\n[![ML216800971 Manx Shearwater © Kirk Zufelt](https://cdn.download.ams.birds.cornell.edu/api/v1/asset/216800971/1200)](https://macaulaylibrary.org/asset/216800971 "ML216800971 Manx Shearwater © Kirk Zufelt")\n\nManx is a migration utility for elasticsearch.  It\'s like [Flyway](https://flywaydb.org/) or [Alembic](https://alembic.sqlalchemy.org/en/latest/), but for elasticsearch.  \n\n> The migration also appears to be quite complex, containing many stopovers and foraging zones\n>\n> -- <cite>[Manx shearwater - Wikipedia](https://en.wikipedia.org/wiki/Manx_shearwater "Manx shearwater - Wikipedia")</cite>\n\n## Features\n* Pure Python implementation\n* Automatic index migration and aliaising\n* Dynamic migration script execution\n\nManx officially supports Python 3.8+.\n\n## Installation\nTo install Manx, simply:\n\n`$ pip install manx`\n\n## Development\nManx uses [poetry](https://python-poetry.org) for dependency management and packaging. To install:\n\n`$ poetry install`\n\nTo build the distributable:\n\n`$ poetry build`\n\nTo publish the package to [PyPI](https://pypi.org/project/manx/):\n\n`$ poetry publish`\n\n### Standards\nManx uses several tools to ensure code standards:\n*  [flake8](https://flake8.pycqa.org/en/latest/): linting\n*  [black](https://pypi.org/project/black/): formatting\n*  [mypy](https://mypy.readthedocs.io/en/stable/): type hinting\n*  [isort](https://timothycrosley.github.io/isort/): import sorting\n\n### Resources\n*  [Poetry](https://python-poetry.org)\n*  [pytest](https://docs.pytest.org/en/stable/index.html)\n*  [pytest-cov](https://github.com/pytest-dev/pytest-cov)\n*  [pytest-asyncio](https://github.com/pytest-dev/pytest-asyncio)\n*  [pytest-mock](https://github.com/pytest-dev/pytest-mock/)\n\n## Image Credit\n[Manx Shearwater](https://ebird.org/species/manshe "Manx Shearwater") *Puffinus puffinus*  \n© Kirk Zufelt  \nJuan Fernández, Valparaíso, Chile | 1 Mar 2020  \n[Macaulay Library ML216800971](https://macaulaylibrary.org/asset/216800971 "Macaulay Library ML216800971") | [eBird S66021223](https://ebird.org/view/checklist/S66021223 "eBird S66021223") | [The Cornelle Lab](https://www.birds.cornell.edu/home "The Cornelle Lab")',
    'author': 'Eric Grunzke',
    'author_email': 'Eric.Grunzke@concentrix.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/text-analytics/open-source/manx',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
