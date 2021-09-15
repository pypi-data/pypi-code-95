# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['easy_file', 'tests']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=5.4.1,<6.0.0', 'orjson>=3.6.3,<4.0.0']

extras_require = \
{'dev': ['tox>=3.20.1,<4.0.0',
         'virtualenv>=20.2.2,<21.0.0',
         'pip>=20.3.1,<21.0.0',
         'twine>=3.3.0,<4.0.0',
         'pre-commit>=2.12.0,<3.0.0',
         'toml>=0.10.2,<0.11.0'],
 'doc': ['mkdocs>=1.1.2,<2.0.0',
         'mkdocs-include-markdown-plugin>=1.0.0,<2.0.0',
         'mkdocs-material>=6.1.7,<7.0.0',
         'mkdocstrings>=0.13.6,<0.14.0',
         'mkdocs-autorefs==0.1.1'],
 'test': ['black==20.8b1',
          'isort==5.6.4',
          'flake8==3.8.4',
          'flake8-docstrings>=1.6.0,<2.0.0',
          'pytest==6.1.2',
          'pytest-cov==2.10.1']}

setup_kwargs = {
    'name': 'easy-file',
    'version': '0.3.2',
    'description': 'Files for humans.',
    'long_description': '# Easy File\n\n\n<p align="center">\n<a href="https://pypi.python.org/pypi/easy_file">\n    <img src="https://img.shields.io/pypi/v/easy_file.svg"\n        alt = "Release Status">\n</a>\n\n<a href="https://github.com/ruslan-rv-ua/easy_file/actions">\n    <img src="https://github.com/ruslan-rv-ua/easy_file/actions/workflows/main.yml/badge.svg?branch=release" alt="CI Status">\n</a>\n\n<!-- a href="https://easy-file.readthedocs.io/en/latest/?badge=latest">\n    <img src="https://readthedocs.org/projects/easy-file/badge/?version=latest" alt="Documentation Status">\n</a -->\n\n</p>\n\n\nFiles for humans\n\n\n* Free software: MIT\n* Documentation: <https://easy-file.readthedocs.io>\n\n\n## Features\n\n* based on `pathlib.Path`\n* UTF-8 by default\n* fast JSON serialization/deserialization with [orjson](https://github.com/ijl/orjson)\n* YAML serialization/deserialization \n\n## Credits\n\nThis package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and the [zillionare/cookiecutter-pypackage](https://github.com/zillionare/cookiecutter-pypackage) project template.\n',
    'author': 'Ruslan Iskov',
    'author_email': 'ruslan.rv.ua@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ruslan-rv-ua/easy_file',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
