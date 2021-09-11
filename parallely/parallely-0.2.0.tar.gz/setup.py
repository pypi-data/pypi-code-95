# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['parallely']

package_data = \
{'': ['*']}

install_requires = \
['asyncio>=3.4.3,<4.0.0', 'nest-asyncio>=1.5.1,<2.0.0', 'pathos>=0.2.8,<0.3.0']

setup_kwargs = {
    'name': 'parallely',
    'version': '0.2.0',
    'description': 'The simplest way to utilize multiple threads, processes, and asynchronous in Python',
    'long_description': '# Parallely - Parallel Python made simple\n\n[![pypi](https://img.shields.io/pypi/v/parallely.svg)](https://pypi.org/project/parallely/)\n[![license](https://img.shields.io/pypi/l/parallely.svg)](https://github.com/mvilstrup/parallely/blob/main/LICENSE)\n[![wheel](https://img.shields.io/pypi/wheel/parallely.svg)](https://pypi.org/project/parallely/)\n[![python](https://img.shields.io/pypi/pyversions/parallely.svg)](https://pypi.org/project/parallely/)\n[![Test Suite](https://github.com/mvilstrup/parallely/workflows/Test%20Suite/badge.svg)](https://github.com/mvilstrup/parallely/actions?query=workflow%3A%22Test+Suite%22)\n[![Coverage Status](https://coveralls.io/repos/github/MVilstrup/parallely/badge.svg?branch=main)](https://coveralls.io/github/MVilstrup/parallely?branch=main)\n[![docs](https://readthedocs.org/projects/parallely/badge/?version=latest)](https://parallely.readthedocs.io/en/latest/?badge=latest)\n\n\n# Installation\n`pip install paralelly`\n\n# Multi Threading\n\n```python\nfrom parallely import threaded\nimport requests\n\n@threaded(max_workers=500)\ndef fetch_data(url):\n    return requests.get(url).json()\n\n# Use the function as usual for fine grained control, testing etc. \nfetch_data("http://www.SOME-WEBSITE.com/data/cool-stuff")\n\n# Use a thread-pool to map over a list of inputs in concurrent manner\nfetch_data.map([\n    "http://www.SOME-WEBSITE.com/data/cool-stuff",\n    "http://www.SOME-WEBSITE.com/data/cool-stuff",\n    "http://www.SOME-WEBSITE.com/data/cool-stuff"\n])\n```\n\n```python\nfrom parallely import threaded\nimport requests\n\n@threaded\ndef fetch(min_val=100, max_val=1000, count=5):\n    return requests.get(f"http://www.randomnumberapi.com/api/v1.0/random?min={min_val}&max={max_val}&count={count}").json()\n\nfetch.map(count=list(range(10)))\n```\n\n# Multi Processing\n\n# Asynchronous\n',
    'author': 'Mikkel Vilstrup',
    'author_email': 'mikkel@vilstrup.dk',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<3.11',
}


setup(**setup_kwargs)
