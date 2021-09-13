# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['naskpy']

package_data = \
{'': ['*']}

install_requires = \
['pendulum>=2.1.2,<3.0.0']

setup_kwargs = {
    'name': 'naskpy',
    'version': '0.1.0',
    'description': 'Tools, modules and functions that I use regularly while coding in Python',
    'long_description': '# NaskPy\nTools, modules and functions that I use regularly while coding in Python\n[![Maintainability](https://api.codeclimate.com/v1/badges/6f79c1172b6dc903377c/maintainability)](https://codeclimate.com/github/naskio/naskpy/maintainability)\n[![codecov](https://codecov.io/gh/naskio/naskpy/branch/main/graph/badge.svg?token=7HY2KN5428)](https://codecov.io/gh/naskio/naskpy)\n[![GitHub issues](https://img.shields.io/github/issues/naskio/naskpy)](https://github.com/naskio/naskpy/issues)\n[![GitHub forks](https://img.shields.io/github/forks/naskio/naskpy)](https://github.com/naskio/naskpy/network)\n[![GitHub stars](https://img.shields.io/github/stars/naskio/naskpy)](https://github.com/naskio/naskpy/stargazers)\n[![GitHub license](https://img.shields.io/github/license/naskio/naskpy)](https://github.com/naskio/naskpy/blob/main/LICENSE)\n',
    'author': 'Mehdi Nassim KHODJA',
    'author_email': 'khodjamehdinassim@gmail.com',
    'maintainer': 'Mehdi Nassim KHODJA',
    'maintainer_email': 'khodjamehdinassim@gmail.com',
    'url': 'https://github.com/naskio/naskpy',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<3.10',
}


setup(**setup_kwargs)
