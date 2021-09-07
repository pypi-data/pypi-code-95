# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['cookiecutter_pypackage_instance']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'cookiecutter-pypackage-instance',
    'version': '0.1.1',
    'description': '🐍 An awesome python package by the name `Cookiecutter Pypackage Instance`',
    'long_description': '<h1 align="center">🐍 Cookiecutter Pypackage Instance</h1>\n\n<p align="center">\n  <a href="https://www.python.org/">\n    <img\n      src="https://img.shields.io/pypi/pyversions/cookiecutter-pypackage-instance"\n      alt="PyPI - Python Version"\n    />\n  </a>\n  <a href="https://pypi.org/project/cookiecutter-pypackage-instance/">\n    <img\n      src="https://img.shields.io/pypi/v/cookiecutter-pypackage-instance"\n      alt="PyPI"\n    />\n  </a>\n  <a href="https://github.com/billsioros/cookiecutter-pypackage-instance/actions/workflows/ci.yml">\n    <img\n      src="https://github.com/billsioros/cookiecutter-pypackage-instance/actions/workflows/ci.yml/badge.svg"\n      alt="CI"\n    />\n  </a>\n  <a href="https://github.com/billsioros/cookiecutter-pypackage-instance/actions/workflows/cd.yml">\n    <img\n      src="https://github.com/billsioros/cookiecutter-pypackage-instance/actions/workflows/cd.yml/badge.svg"\n      alt="CD"\n    />\n  </a>\n  <a href="https://results.pre-commit.ci/latest/github/billsioros/cookiecutter-pypackage-instance/master">\n    <img\n      src="https://results.pre-commit.ci/badge/github/billsioros/cookiecutter-pypackage-instance/master.svg"\n      alt="pre-commit.ci status"\n    />\n  </a>\n  <a href="https://codecov.io/gh/billsioros/cookiecutter-pypackage-instance">\n    <img\n      src="https://codecov.io/gh/billsioros/cookiecutter-pypackage-instance/branch/master/graph/badge.svg?token=coLOL0j6Ap"\n      alt="Test Coverage"/>\n  </a>\n  <a href="https://opensource.org/licenses/MIT">\n    <img\n      src="https://img.shields.io/pypi/l/cookiecutter-pypackage-instance"\n      alt="PyPI - License"\n    />\n  </a>\n  <a href="https://gitpod.io/from-referrer/">\n    <img\n      src="https://img.shields.io/badge/Open%20on-Gitpod-blue?logo=gitpod&style=flat"\n      alt="Open on Gitpod"\n    />\n  </a>\n  <a href="https://github.com/billsioros/cookiecutter-pypackage">\n    <img\n      src="https://img.shields.io/badge/cookiecutter-template-D4AA00.svg?style=flat&logo=cookiecutter"\n      alt="Cookiecutter Template">\n  </a>\n  <a href="https://app.renovatebot.com/dashboard#github/billsioros/cookiecutter-pypackage-instance">\n    <img\n      src="https://img.shields.io/badge/renovate-enabled-brightgreen.svg?style=flat&logo=renovatebot"\n      alt="Renovate - Enabled">\n  </a>\n  <a href="https://www.buymeacoffee.com/billsioros">\n    <img\n      src="https://img.shields.io/badge/Buy%20me%20a-coffee-FFDD00.svg?style=flat&logo=buymeacoffee"\n      alt="Buy me a coffee">\n  </a>\n</p>\n\n## Example Usage\n\n```python\n>>> from cookiecutter_pypackage_instance import cookiecutter_pypackage_instance\n```\n\n## Features\n\n- TODO\n\n## Documentation\n\nThe project\'s documentation can be found [here](https://billsioros.github.io/cookiecutter-pypackage-instance/).\n\n## Installation\n\n```bash\npip install cookiecutter-pypackage-instance\n```\n\n## Supporting the project\n\nFeel free to [**Buy me a coffee! ☕**](https://www.buymeacoffee.com/billsioros).\n\n## Contributing\n\nIf you would like to contribute to the project, please go through the [Contributing Guidelines](https://billsioros.github.io/cookiecutter-pypackage-instance/latest/CONTRIBUTING/) first.\n\n## Contributors ✨\n\nThanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):\n\n<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->\n<!-- prettier-ignore-start -->\n<!-- markdownlint-disable -->\n\n<!-- markdownlint-restore -->\n<!-- prettier-ignore-end -->\n<!-- ALL-CONTRIBUTORS-LIST:END -->\n\nThis project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!\n\n## Credits\n\nThis package was created with [Cookiecutter](https://github.com/cookiecutter/cookiecutter) and the [billsioros/cookiecutter-pypackage](https://github.com/billsioros/cookiecutter-pypackage) cookiecutter template.\n',
    'author': 'Vasilis Sioros',
    'author_email': 'billsioros97@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://billsioros.github.io/cookiecutter-pypackage-instance',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
