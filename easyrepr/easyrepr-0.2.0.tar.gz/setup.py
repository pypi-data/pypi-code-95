# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['easyrepr']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'easyrepr',
    'version': '0.2.0',
    'description': 'Python decorator to automatically generate repr strings',
    'long_description': "# easyrepr\n\n[![Read the Docs][rtd-badge]][rtd-link]\n\nPython decorator to automatically generate repr strings\n\n[rtd-badge]: https://readthedocs.org/projects/easyrepr/badge/\n[rtd-link]: https://easyrepr.readthedocs.io/en/latest/\n\n## Example\n\n```pycon\n>>> class UseEasyRepr:\n...     def __init__(self, foo, bar):\n...         self.foo = foo\n...         self.bar = bar\n...     @easyrepr\n...     def __repr__(self):\n...         ...\n...\n>>> x = UseEasyRepr(1, 2)\n>>> repr(x)\n'UseEasyRepr(foo=1, bar=2)'\n```\n\n## Installation\n\n```console\n$ pip install easyrepr\n```\n",
    'author': 'Chris Bouchard',
    'author_email': 'chris@upliftinglemma.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/chrisbouchard/easyrepr',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
