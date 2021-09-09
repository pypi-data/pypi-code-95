# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pypj', 'pypj.resources', 'pypj.task']

package_data = \
{'': ['*']}

install_requires = \
['single-source>=0.2.0,<0.3.0']

entry_points = \
{'console_scripts': ['pypj = pypj.main:main']}

setup_kwargs = {
    'name': 'pypj',
    'version': '0.5.2',
    'description': 'Python project initializer',
    'long_description': '![Pypj Logo](https://raw.githubusercontent.com/edge-minato/pypj/main/doc/img/logo.png)\n\n[![pypi version](https://img.shields.io/pypi/v/pypj.svg?style=flat)](https://pypi.org/pypi/pypj/)\n[![python versions](https://img.shields.io/pypi/pyversions/pypj.svg?style=flat)](https://pypi.org/pypi/pypj/)\n[![format](https://img.shields.io/pypi/format/pypj.svg?style=flat)](https://pypi.org/pypi/pypj/)\n[![license](https://img.shields.io/pypi/l/pypj.svg?style=flat)](https://github.com/edge-minato/pypj/blob/master/LICENSE)\n[![Unittest](https://github.com/edge-minato/pypj/actions/workflows/unittest.yml/badge.svg)](https://github.com/edge-minato/pypj/actions/workflows/unittest.yml)\n[![codecov](https://codecov.io/gh/edge-minato/pypj/branch/main/graph/badge.svg?token=YDZAMKUNS0)](https://codecov.io/gh/edge-minato/pypj)\n[![Code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black")\n\n`Pypj` provides you an initialized modern python project. All the basic dev package installations, their configurations, and test workflows will be done, so we can focus on coding. All you have to do is install `poetry` and hit `pypj`, name your project.\n\n## What will be provided\n\nThe _"Modern"_ project settings `Pypj` suggests is following. We understand some developers prefer another tools, and you can remove or customize the packages to be installed.\n\n### Environment\n\n- Package manager: [`poetry`](https://github.com/python-poetry/poetry)\n- Formatter: [`black`](https://github.com/psf/black)\n- Linter: [`pflake8`](https://github.com/csachs/pyproject-flake8)\n- Type linter: [`mypy`](https://github.com/python/mypy)\n- Import formatter: [`isort`](https://github.com/PyCQA/isort)\n- Test framework:\n  - [`pytest`](https://github.com/pytest-dev/pytest)\n    - [`pytest-cov`](https://github.com/pytest-dev/pytest-cov)\n    - [`pytest-mock`](https://github.com/pytest-dev/pytest-mock)\n  - [`tox`](https://github.com/tox-dev/tox)\n    - [`tox-gh-actions`](https://github.com/ymyzk/tox-gh-actions)\n\n### Coding format\n\n- Max line length: `119` as default\n- Type hinting: `required`\n- And some detailed configures\n\n### Other features\n\n- Single filed configurations on `pyproject.toml`\n- Single sourced versioning: [`single-source`](https://github.com/rabbit72/single-source)\n- Command alias: [`make`](https://www.gnu.org/software/make/)\n- CI/CD\n  - unittest workflow\n\n### Directory structure\n\nDo you think the directory tree looks poor? Because all configurations are aggregated in `pyproject.toml`, we don\'t need any tool specific configuration files.\n\n```\n$ tree -a -L 1\nmy-package/\n├── .github\n├── .venv\n├── .vscode\n├── Makefile\n├── README.md\n├── my-package\n├── poetry.lock\n├── pyproject.toml\n└── tests\n```\n\n## Requirements\n\n- `python3`\n- `poetry`\n\n## Installation\n\n```sh\npip install pypj\n```\n\n## Usage\n\n```\n$ pypj\n\n┌─┐┬ ┬┌─┐┬\n├─┘└┬┘├─┘│    python : 3.8.5\n┴   ┴ ┴ └┘    poetry : 1.1.7\n\nPackage name: my-package\nDo you want to custom setting? (y/N):\nTask: Initialize package: my-package\n  Command: poetry new my-package ✨\n  Poetry new done 🚀\n  Command: poetry config virtualenvs.in-project true ✨\n  Command: poetry add -D black ✨\n  Command: poetry add -D pyproject-flake8 ✨\n  Command: poetry add -D mypy ✨\n  Command: poetry add -D isort ✨\n  Command: poetry add -D pytest ✨\n  Command: poetry add -D tox ✨\n  Command: poetry add -D pytest-cov ✨\n  Command: poetry add -D pytest-mock ✨\n  Command: poetry add -D tox-gh-actions ✨\n  Create : my-package ✨\nTask: Configure vscode settings\n  Create : .vscode/settings.json ✨\nTask: Configure pyproject.toml settings\n  Write  : pyproject.toml ✨\n  COnfigure: __init__.py\nTask: Create makefile\n  Create : Makefile ✨\nTask: Create github actions\n  Create : unittest.yml ✨\nTask: Create README.md\n  Create : README.md ✨\n\nComplete! 🚀\nLet\'s make the world better! ✨😋🐍🌎\n```\n\n## Example configurations on `pyproject.toml`\n\nWith default setting, this kind of `pyproject.toml` file will be generated.\n\n```toml\n[tool.poetry]\nname = "my-package"\nversion = "0.1.0"\ndescription = ""\nauthors = ["you <you@example.com>"]\n\n[tool.poetry.dependencies]\npython = "^3.8"\n\n[tool.poetry.dev-dependencies]\npytest = "^5.2"\nblack = "^21.8b0"\npyproject-flake8 = "^0.0.1-alpha.2"\nmypy = "^0.910"\nisort = "^5.9.3"\npytest-cov = "^2.12.1"\n\n[build-system]\nrequires = ["poetry-core>=1.0.0"]\nbuild-backend = "poetry.core.masonry.api"\n\n[tool.black]\nline-length = 119\nexclude = \'\'\'\n(\n    migrations\n    | .mypy_cache\n    | .pytest_cache\n    | .tox\n    | venv\n)\n\'\'\'\n\n[tool.flake8]\nmax-line-length = 119\nmax-complexity = 10\n\n[tool.mypy]\n# common\npython_version = 3.8\nshow_column_numbers = true\nshow_error_context = true\nignore_missing_imports = true\ncheck_untyped_defs = true\ndisallow_untyped_defs = true\n# warning\nwarn_return_any = true\nwarn_unused_configs = true\nwarn_redundant_casts = true\n\n[tool.isort]\nprofile = "black"\nline_length = 119\n```\n\n## Supported python versions\n\n- Supported: `3.7`, `3.8`, `3.9`\n- Is going to be supported: `3.10`\n- Not supported: `3.6` or less\n\n**NOTE**: According to [Status of Python branches](https://devguide.python.org/#status-of-python-branches), the EoL of Python 3.6 is `2021-12-23`.\n',
    'author': 'edge-minato',
    'author_email': 'edge.minato@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/edge-minato/pypj',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
