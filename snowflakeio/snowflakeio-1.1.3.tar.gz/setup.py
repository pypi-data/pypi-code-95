# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['snowflakeio', 'snowflakeio.web']

package_data = \
{'': ['*']}

install_requires = \
['beautifulsoup4>=4.10.0,<5.0.0',
 'lxml>=4.6.3,<5.0.0',
 'numpy>=1.21.2,<2.0.0',
 'pandas>=1.3.2,<2.0.0',
 'requests>=2.26.0,<3.0.0']

setup_kwargs = {
    'name': 'snowflakeio',
    'version': '1.1.3',
    'description': 'Snowflake IO, a Pythonic Algorithmic Trading Library',
    'long_description': '# snowflakeio\n\n<div align="center">\n\n[![Build status](https://github.com/bradleycm/snowflakeio/workflows/build/badge.svg?branch=master&event=push)](https://github.com/bradleycm/snowflakeio/actions?query=workflow%3Abuild)\n[![Python Version](https://img.shields.io/pypi/pyversions/snowflakeio.svg)](https://pypi.org/project/snowflakeio/)\n[![Dependencies Status](https://img.shields.io/badge/dependencies-up%20to%20date-brightgreen.svg)](https://github.com/bradleycm/snowflakeio/pulls?utf8=%E2%9C%93&q=is%3Apr%20author%3Aapp%2Fdependabot)\n\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![Security: bandit](https://img.shields.io/badge/security-bandit-green.svg)](https://github.com/PyCQA/bandit)\n[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/bradleycm/snowflakeio/blob/master/.pre-commit-config.yaml)\n[![Semantic Versions](https://img.shields.io/badge/%20%20%F0%9F%93%A6%F0%9F%9A%80-semantic--versions-e10079.svg)](https://github.com/bradleycm/snowflakeio/releases)\n[![License](https://img.shields.io/github/license/bradleycm/snowflakeio)](https://github.com/bradleycm/snowflakeio/blob/master/LICENSE)\n\nSnowflake IO, a Pythonic Algorithmic Trading Library\n\n</div>\n\n\n## Installation\n\n```bash\npip install -U snowflakeio\n```\n\nor install with `Poetry`\n\n```bash\npoetry add snowflakeio\n```\n\n## 📈 Releases\n\nYou can see the list of available releases on the [GitHub Releases](https://github.com/bradleycm/snowflakeio/releases) page.\n\nWe follow [Semantic Versions](https://semver.org/) specification.\n\nWe use [`Release Drafter`](https://github.com/marketplace/actions/release-drafter). As pull requests are merged, a draft release is kept up-to-date listing the changes, ready to publish when you’re ready. With the categories option, you can categorize pull requests in release notes using labels.\n\n### List of labels and corresponding titles\n\n|               **Label**               |  **Title in Releases**  |\n| :-----------------------------------: | :---------------------: |\n|       `enhancement`, `feature`        |       🚀 Features       |\n| `bug`, `refactoring`, `bugfix`, `fix` | 🔧 Fixes & Refactoring  |\n|       `build`, `ci`, `testing`        | 📦 Build System & CI/CD |\n|              `breaking`               |   💥 Breaking Changes   |\n|            `documentation`            |    📝 Documentation     |\n|            `dependencies`             | ⬆️ Dependencies updates |\n\nYou can update it in [`release-drafter.yml`](https://github.com/bradleycm/snowflakeio/blob/master/.github/release-drafter.yml).\n\nGitHub creates the `bug`, `enhancement`, and `documentation` labels for you. Dependabot creates the `dependencies` label. Create the remaining labels on the Issues tab of your GitHub repository, when you need them.\n\n## 🛡 License\n\n[![License](https://img.shields.io/github/license/bradleycm/snowflakeio)](https://github.com/bradleycm/snowflakeio/blob/master/LICENSE)\n\nThis project is licensed under the terms of the `GNU GPL v3.0` license. See [LICENSE](https://github.com/bradleycm/snowflakeio/blob/master/LICENSE) for more details.\n\n## 📃 Citation\n\n```bibtex\n@misc{snowflakeio,\n  author = {bradleycm},\n  title = {Snowflake IO, a Pythonic Algorithmic Trading Library},\n  year = {2021},\n  publisher = {GitHub},\n  journal = {GitHub repository},\n  howpublished = {\\url{https://github.com/bradleycm/snowflakeio}}\n}\n```\n',
    'author': 'bradleycm',
    'author_email': 'chris@riftpay.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/bradleycm/snowflakeio',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
