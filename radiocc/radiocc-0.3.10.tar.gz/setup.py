# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['radiocc', 'radiocc.old']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=5.4.1,<6.0.0',
 'click>=8.0.1,<9.0.0',
 'colored>=1.4.2,<2.0.0',
 'dotmap>=1.3.24,<2.0.0',
 'envtoml>=0.1.2,<0.2.0',
 'matplotlib>=3.4.3,<4.0.0',
 'nptyping>=1.4.3,<2.0.0',
 'numpy>=1.21.2,<2.0.0',
 'pandas>=1.3.2,<2.0.0',
 'pudb>=2021.1,<2022.0',
 'pytest-sugar>=0.9.4,<0.10.0',
 'pytest>=6.2.5,<7.0.0',
 'ruamel.yaml>=0.17.16,<0.18.0',
 'scipy>=1.7.1,<2.0.0',
 'spiceypy>=4.0.2,<5.0.0',
 'types-PyYAML>=5.4.10,<6.0.0',
 'types-click>=7.1.5,<8.0.0']

entry_points = \
{'console_scripts': ['radiocc = radiocc.cli:main']}

setup_kwargs = {
    'name': 'radiocc',
    'version': '0.3.10',
    'description': 'Radio occultations',
    'long_description': "# radiocc\n\n[![license badge]][license file]\n[![version badge]][repo url]\n[![python badge]][python url]\n[![coverage badge]][coverage url]\n[![pre-commit badge]][pre-commit url]\n\n> Radio occulation\n\n---\n\n[Installation](#installation) |\n[Roadmap](#roadmap) |\n[Contributing](#contributing) |\n[License](#license)\n\n---\n\n## Installation\n\nThe code is still in development, hence you can only get it on\n[ROB Gitlab repo][repo url]\n\nYou need to:\n\n+ clone it\n+ download [poetry][poetry url] (a tool for dependency management and packaging\n  in Python)\n+ run\n  ```sh\n  poetry install\n  ```\n  inside the project to install the dependencies in a virtual environment (it\n  should be done automatically, long time I didn't do it, if it does not let us\n  know and we will do it together)\n+ to check the virtual env is correctly set, use\n  ```sh\n  poetry env info\n  ```\n  and confirm you have something similar to:\n  ```sh\n  Virtualenv\n  Python:         3.9.6\n  Implementation: CPython\n  Path:           /home/greg/.cache/pypoetry/virtualenvs/radiocc-6zeAPCek-py3.9\n  Valid:          True\n  ```\n+ run\n  ```sh\n  poetry shell\n  ```\n  to activate the virtual environment, it can be useful for IDE\n  and linters but not necessary because it is automatically activated at runtime.\n+ create a folder `RESULTS` and a folder `TO_PROCESS` and place in the latter\n  your *MEX* or *MVN* scenarios to be run run `poetry run radiocc` to run the code\n  automatically on the scenarios to be processed.\n\n## Roadmap\n\n+ improve old code for lisibility, portability and testing\n+ improve CLI interface for parameter tuning\n+ provide GUI interface for parameter tuning\n+ provide GUI tool on graphs to set thresholds and corrections\n+ provide a [`pip`][pip url] library and binary installation\n\n## Contributing\n\n### Evaluate code before commiting\n\nWe use the powerful tool [pre-commit][pre-commit url] to automatically run a\nbattery of tests on the code at commit runtime to:\n\n+ avoid pushing code with warnings and errors\n+ unify code formatting between developpers\n\nThe list of tests and hook scripts can be found here.\n\nThey consist in:\n\n+ few git and file-system checks\n+ [`flake8`][flake8 url] (python static linter)\n+ [`isort`][isort url] (python imports linter & fixer)\n+ [`mypy`][mypy url] (python type checker)\n+ [`black`][black url] (python code fixer)\n+ running tests with [`pytest`][pytest url]\n\nYou can install this development environment using\n\n```sh\npoetry run pre-commit install\n```\n\n### Commiting\n\nYou can fork and ask for pull request on the `dev` branch (or any other excepted\nthe `main` branch).\n\nDepending on your access rights, you can also create a new\nbranch from `dev`, develop on it and ask for a merge into the `dev` branch.\n\n## License\n\nLicensed under the [Apache 2.0 license][license file].\n\n[repo url]: https://gitlab-as.oma.be/gregoireh/radiocc\n[pre-commit file]: https://gitlab-as.oma.be/gregoireh/radiocc/-/raw/main/.pre-commit-config.yaml\n[license file]: https://gitlab-as.oma.be/gregoireh/radiocc/-/raw/main/LICENSE\n[license badge]: https://img.shields.io/badge/License-Apache%202.0-blue.svg\n[coverage badge]: https://img.shields.io/badge/coverage-0%25-red\n[coverage url]: https://github.com/pytest-dev/pytest-cov\n[version badge]: https://img.shields.io/badge/version-0.3.10-blue\n[python url]: https://www.python.org/\n[python badge]: https://img.shields.io/badge/python->=3.9,<3.10-blue\n[pre-commit url]: https://pre-commit.com\n[pre-commit badge]: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white\n[poetry url]: https://python-poetry.org/docs\n[flake8 url]: https://flake8.pycqa.org/en/latest\n[isort url]: https://github.com/timothycrosley/isort\n[mypy url]: http://mypy-lang.org\n[black url]: https://github.com/psf/black\n[pytest url]: https://docs.pytest.org/en/latest\n[pip url]: https://pip.pypa.io/en/stable/\n",
    'author': 'Ananya Krishnan',
    'author_email': 'ananyakrishnaniiserk@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab-as.oma.be/gregoireh/radiocc',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<3.10',
}


setup(**setup_kwargs)
