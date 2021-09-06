# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['poetry',
 'poetry.core',
 'poetry.core._vendor',
 'poetry.core._vendor.attr',
 'poetry.core._vendor.jsonschema',
 'poetry.core._vendor.jsonschema.benchmarks',
 'poetry.core._vendor.lark',
 'poetry.core._vendor.lark.__pyinstaller',
 'poetry.core._vendor.lark.parsers',
 'poetry.core._vendor.lark.tools',
 'poetry.core._vendor.packaging',
 'poetry.core._vendor.pyrsistent',
 'poetry.core._vendor.tomlkit',
 'poetry.core.exceptions',
 'poetry.core.json',
 'poetry.core.masonry',
 'poetry.core.masonry.builders',
 'poetry.core.masonry.utils',
 'poetry.core.packages',
 'poetry.core.packages.constraints',
 'poetry.core.packages.utils',
 'poetry.core.pyproject',
 'poetry.core.semver',
 'poetry.core.spdx',
 'poetry.core.toml',
 'poetry.core.utils',
 'poetry.core.vcs',
 'poetry.core.version',
 'poetry.core.version.grammars',
 'poetry.core.version.pep440']

package_data = \
{'': ['*'],
 'poetry.core._vendor.jsonschema': ['schemas/*'],
 'poetry.core._vendor.lark': ['grammars/*'],
 'poetry.core.json': ['schemas/*'],
 'poetry.core.spdx': ['data/*']}

install_requires = \
['tomlkit>=0.7.2,<0.8.0']

extras_require = \
{':python_version < "3.8"': ['importlib-metadata>=1.7.0'],
 ':python_version >= "3.6" and python_version < "3.7"': ['dataclasses>=0.8']}

setup_kwargs = {
    'name': 'relaxed-poetry-core',
    'version': '0.1.0',
    'description': 'Fork of poetry-core, with some relaxations',
    'long_description': '# About This Fork\nThis is a poetry-core fork with some relaxations and additional features \nPlease see [Relaxed Poetry](https://github.com/bennylut/relaxed-poetry) for more information\n\n**The rest of this README left as is from the original Poetry Core README**\n\n# Poetry Core\n[![PyPI version](https://img.shields.io/pypi/v/poetry-core)](https://pypi.org/project/poetry-core/)\n[![Python Versions](https://img.shields.io/pypi/pyversions/poetry-core)](https://pypi.org/project/poetry-core/)\n[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![](https://github.com/python-poetry/poetry-core/workflows/Tests/badge.svg)](https://github.com/python-poetry/poetry-core/actions?query=workflow%3ATests)\n\nA [PEP 517](https://www.python.org/dev/peps/pep-0517/) build backend implementation developed for\n[Poetry](https://github.com/python-poetry/poetry). This project is intended to be a light weight, fully compliant,\nself-contained package allowing PEP 517 compatible build frontends to build Poetry managed projects.\n\n## Usage\nIn most cases, the usage of this package is transparent to the end-user as it is either made use by Poetry itself\nor a PEP 517 frontend (eg: `pip`).\n\nIn order to enable the use `poetry-core` as your build backend, the following snippet must be present in your\nproject\'s `pyproject.toml` file.\n\n```toml\n[build-system]\nrequires = ["poetry-core"]\nbuild-backend = "poetry.core.masonry.api"\n```\n\nOnce this is present, a PEP 517 frontend like `pip` can build and install your project from source without the need\nfor Poetry or any of it\'s dependencies.\n\n```shell\n# install to current environment\npip install /path/to/poetry/managed/project\n\n# build a wheel package\npip wheel /path/to/poetry/managed/project\n```\n\n## Why is this required?\nPrior to the release of version `1.1.0`, Poetry was a build as a project management tool that included a PEP 517\nbuild backend. This was inefficient and time consuming in majority cases a PEP 517 build was required. For example,\nboth `pip` and `tox` (with isolated builds) would install Poetry and all dependencies it required. Most of these\ndependencies are not required when the objective is to simply build either a source or binary distribution of your\nproject.\n\nIn order to improve the above situation, `poetry-core` was created. Shared functionality pertaining to PEP 517 build\nbackends, including reading lock file, `pyproject.toml` and building wheel/sdist, were implemented in this package.  This\nmakes PEP 517 builds extremely fast for Poetry managed packages.\n',
    'author': 'bennylut',
    'author_email': 'None',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/bennylut/relaxed-poetry-core',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
