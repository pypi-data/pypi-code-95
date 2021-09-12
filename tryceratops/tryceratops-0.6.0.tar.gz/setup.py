# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['tryceratops',
 'tryceratops.analyzers',
 'tryceratops.files',
 'tryceratops.fixers',
 'tryceratops.violations']

package_data = \
{'': ['*']}

install_requires = \
['click>=7,<8', 'toml>=0.10.2,<0.11.0']

entry_points = \
{'console_scripts': ['tryceratops = tryceratops.__main__:main'],
 'flake8.extension': ['TC = tryceratops.flake_plugin:TryceratopsAdapterPlugin']}

setup_kwargs = {
    'name': 'tryceratops',
    'version': '0.6.0',
    'description': 'A linter to manage your exception like a PRO!',
    'long_description': '<p align="center">\n    <img src="https://raw.githubusercontent.com/guilatrova/tryceratops/main/img/logo.png">\n</p>\n\n<h2 align="center">Manage your exceptions in Python like a PRO</h2>\n\n<p align="center">\n\n  <a href="https://github.com/guilatrova/tryceratops/actions"><img alt="Actions Status" src="https://github.com/guilatrova/tryceratops/workflows/CI/badge.svg"></a>\n  <a href="https://pypi.org/project/tryceratops/"><img alt="PyPI" src="https://img.shields.io/pypi/v/tryceratops"/></a>\n  <a href="https://github.com/relekang/python-semantic-release"><img alt="Semantic Release" src="https://img.shields.io/badge/%20%20%F0%9F%93%A6%F0%9F%9A%80-semantic--release-e10079.svg"></a>\n  <a href="https://github.com/guilatrova/tryceratops/blob/main/LICENSE"><img alt="GitHub" src="https://img.shields.io/github/license/guilatrova/tryceratops"/></a>\n  <a href="https://pepy.tech/project/tryceratops/"><img alt="Downloads" src="https://static.pepy.tech/personalized-badge/tryceratops?period=total&units=international_system&left_color=grey&right_color=blue&left_text=%F0%9F%A6%96%20Downloads"/></a>\n  <a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"/></a>\n  <a href="https://github.com/guilatrova/tryceratops"><img alt="try/except style: tryceratops" src="https://img.shields.io/badge/try%2Fexcept%20style-tryceratops%20%F0%9F%A6%96%E2%9C%A8-black" /></a>\n  <a href="https://open.vscode.dev/guilatrova/tryceratops"><img alt="Open in Visual Studio Code" src="https://open.vscode.dev/badges/open-in-vscode.svg"/></a>\n\n</p>\n\nInspired by [this blog post](https://blog.guilatrova.dev/handling-exceptions-in-python-like-a-pro/).\n\nI shared [the building process of this tool here](https://blog.guilatrova.dev/project-tryceratops/).\n\n> “For those who like dinosaurs 🦖 and clean try/except ✨ blocks.”\n\n- [Installation and usage](#installation-and-usage)\n  - [Installation](#installation)\n  - [Usage](#usage)\n  - [`flake8` Plugin](#flake8-plugin)\n- [Violations](#violations)\n  - [Autofix support](#autofix-support)\n  - [Ignoring violations](#ignoring-violations)\n  - [Configuration](#configuration)\n- [Pre-commit](#pre-commit)\n- [Show your style](#show-your-style)\n- [Extra Resources](#extra-resources)\n- [Contributing](#contributing)\n- [Change log](#change-log)\n- [License](#license)\n- [Credits](#credits)\n\n---\n\n## Installation and usage\n\n### Installation\n\n```\npip install tryceratops\n```\n\n### Usage\n\n```\ntryceratops [filename or dir...]\n```\n\nYou can enable experimental analyzers by running:\n\n```\ntryceratops --experimental [filename or dir...]\n```\n\nYou can ignore specific violations by using: `--ignore TCXXX` repeatedly:\n\n```\ntryceratops --ignore TC201 --ignore TC202 [filename or dir...]\n```\n\nYou can exclude dirs by using: `--exclude dir/path` repeatedly:\n\n```\ntryceratops --exclude tests --exclude .venv [filename or dir...]\n```\n\nYou can also autofix some violations:\n\n```\ntryceratops --autofix [filename or dir...]\n```\n\n![example](https://raw.githubusercontent.com/guilatrova/tryceratops/main/img/tryceratops-example3.gif)\n\n### [`flake8`](https://github.com/PyCQA/flake8) Plugin\n\n🦖 Tryceratops is also a plugin for `flake8`, so you can:\n\n```\n❯ flake8 --select TC src/tests/samples/violations/call_raise_vanilla.py\nsrc/tests/samples/violations/call_raise_vanilla.py:13:9: TC002 Create your own exception\nsrc/tests/samples/violations/call_raise_vanilla.py:13:9: TC003 Avoid specifying long messages outside the exception class\nsrc/tests/samples/violations/call_raise_vanilla.py:21:9: TC201 Simply use \'raise\' without specifying exception object again\n```\n\n## Violations\n\nAll violations and its descriptions can be found in [docs](https://github.com/guilatrova/tryceratops/tree/main/docs/violations).\n\n### Autofix support\n\nSo far, autofix only supports violations: [TC200](docs/violations/TC200.md), [TC201](docs/violations/TC201.md), and [TC400](docs/violations/TC400.md).\n\n### Ignoring violations\n\nIf you want to ignore a violation in a specific file, you can either:\n\n- Add a comment with `noqa` to the top of the file you want to ignore\n- Add a comment with `noqa` to the line you want to ignore\n- Add a comment with `noqa: CODE` to the line you want to ignore a specific violation\n\nExample:\n\n```py\ndef verbose_reraise_1():\n    try:\n        a = 1\n    except Exception as ex:\n        raise ex  # noqa: TC202\n```\n\n### Configuration\n\nYou can set up a `pyproject.toml` file to set rules.\nThis is useful to avoid reusing the same CLI flags over and over again and helps to define the structure of your project.\n\nExample:\n\n```toml\n[tool.tryceratops]\nexclude = ["samples"]\nignore = ["TC002", "TC200", "TC300"]\nexperimental = true\n```\n\nCLI flags always overwrite the config file.\n\n## Pre-commit\n\nIf you wish to use pre-commit, add this:\n\n```yaml\n  - repo: https://github.com/guilatrova/tryceratops\n    rev: v0.6.0\n    hooks:\n      - id: tryceratops\n```\n\n## Show your style\n\n[![try/except style: tryceratops](https://img.shields.io/badge/try%2Fexcept%20style-tryceratops%20%F0%9F%A6%96%E2%9C%A8-black)](https://github.com/guilatrova/tryceratops)\n\nAdd this fancy badge to your project\'s `README.md`:\n\n```md\n[![try/except style: tryceratops](https://img.shields.io/badge/try%2Fexcept%20style-tryceratops%20%F0%9F%A6%96%E2%9C%A8-black)](https://github.com/guilatrova/tryceratops)\n```\n\n## Extra Resources\n\nIf you want to read more about:\n\n- [How to structure exceptions in Python 🐍 🏗️ 💣](https://blog.guilatrova.dev/how-to-structure-exception-in-python-like-a-pro/)\n- [Book: Effective Python](https://amzn.to/3bEVHpG)\n\n## Contributing\n\nThank you for considering making Tryceratops better for everyone!\n\nRefer to [Contributing docs](docs/CONTRIBUTING.md).\n\n## Change log\n\nSee [CHANGELOG](CHANGELOG.md).\n\n## License\n\nMIT\n\n## Credits\n\nThanks to God for the inspiration 🙌 ☁️ ☀️\n\nLogo icon was made by [https://www.freepik.com](Freepik)\n\nThe [black](https://github.com/psf/black) project for insights.\n',
    'author': 'Guilherme Latrova',
    'author_email': 'hello@guilatrova.dev',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/guilatrova/tryceratops',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
