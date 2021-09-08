# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pnq']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'pnq',
    'version': '0.0.4',
    'description': '',
    'long_description': '# pnq\npnq is a Python implementation like Language Integrated Query (LINQ).\n\n# Requirement\n\n- Python 3.7+\n\n# Installation\n\n``` shell\n```\n\n# Getting started\n\n\n# Setup\n\n\n# 調査\nLinqライクなライブラリで、type hintと親和性があるライブラリがあるか調査した。\n\n## pyfunctional\n- https://github.com/EntilZha/PyFunctional\n- star: 1.9k\n\n機能は多い。\n型情報は伝搬しない。\n\n\n## pyLINQ star: 2\ntype hintが効かない。機能は少なくstarも少ない\n\n## linqish\nプロジェクトはもう死んでいる\n\n',
    'author': 'sasano8',
    'author_email': 'y-sasahara@ys-method.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
