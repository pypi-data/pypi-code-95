# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['isabelle_client']

package_data = \
{'': ['*']}

extras_require = \
{':python_version < "3.7"': ['dataclasses']}

setup_kwargs = {
    'name': 'isabelle-client',
    'version': '0.2.8',
    'description': 'A client to Isabelle proof assistant server',
    'long_description': "[![PyPI version](https://badge.fury.io/py/isabelle-client.svg)](https://badge.fury.io/py/isabelle-client) [![CircleCI](https://circleci.com/gh/inpefess/isabelle-client.svg?style=svg)](https://circleci.com/gh/inpefess/isabelle-client) [![Documentation Status](https://readthedocs.org/projects/isabelle-client/badge/?version=latest)](https://isabelle-client.readthedocs.io/en/latest/?badge=latest) [![codecov](https://codecov.io/gh/inpefess/isabelle-client/branch/master/graph/badge.svg)](https://codecov.io/gh/inpefess/isabelle-client)\n\nDocumentation is hosted [here](https://isabelle-client.readthedocs.io).\n\nIf you're writing a research paper, you can cite Isabelle client (and Isabelle 2021) in the [following way](https://dblp.org/rec/conf/mkm/LiskaLNRSSSW21.bib).\n\n# Video example\n\n![video tutorial](https://github.com/inpefess/isabelle-client/blob/master/examples/tty.gif).\n",
    'author': 'Boris Shminke',
    'author_email': 'boris@shminke.ml',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/inpefess/isabelle-client',
    'packages': packages,
    'package_data': package_data,
    'extras_require': extras_require,
    'python_requires': '>=3.6.1,<4.0',
}


setup(**setup_kwargs)
