# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['simplethread']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'simplethread',
    'version': '1.0.1',
    'description': "Some useful utilities for Python's threading module",
    'long_description': "Simple Thread\n=============\n[![pipeline status][pipeline]][homepage]\n[![coverage report][coverage]][homepage]\n[![latest version][version]][pypi]\n[![python requires][pyversions]][pypi]\n\nSome useful utilities for Python's `threading` module.\n\nRequirements\n------------\nPython 3.8+\n\nInstallation\n------------\n```\n$ pip install simplethread\n```\n\nDistribution\n------------\nThis project is licensed under the terms of the [MIT License](LICENSE).\n\nLinks\n-----\n- Code: <https://gitlab.com/amalchuk/simplethread>\n- GitHub mirror: <https://github.com/amalchuk/simplethread>\n\n[homepage]: <https://gitlab.com/amalchuk/simplethread>\n[pypi]: <https://pypi.org/project/simplethread>\n[pipeline]: <https://gitlab.com/amalchuk/simplethread/badges/master/pipeline.svg?style=flat-square>\n[coverage]: <https://gitlab.com/amalchuk/simplethread/badges/master/coverage.svg?style=flat-square>\n[version]: <https://img.shields.io/pypi/v/simplethread?color=blue&style=flat-square>\n[pyversions]: <https://img.shields.io/pypi/pyversions/simplethread?color=blue&style=flat-square>\n",
    'author': 'Andrew Malchuk',
    'author_email': 'andrew.malchuk@yandex.ru',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/amalchuk/simplethread',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
