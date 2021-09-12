# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dataclass_applicative']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'dataclass-applicative',
    'version': '0.1.0',
    'description': '',
    'long_description': "# `dataclass-applicative` --- treating dataclasses like containers\n\nThis package provides functions for manipulating dataclasses as containers.\n\n## Documentation\n\nThe documentation is hosted on [ReadTheDocs][1], and the source code\nfor that documentation is available [here](docs/index.rst).\n\n## Quick start\n\nGiven a dataclass,\n\n    >>> from dataclasses import dataclass\n    >>> from dataclass_applicative import amap, fmap, gather, pure, names, values\n    >>> @dataclass\n    ... class F:\n    ...     x: object\n    ...     y: object\n    ...     z: object\n\nwe can list its fields;\n\n    >>> list(names(F))\n    ['x', 'y', 'z']\n\nlist its values;\n\n    >>> list(values(F(1, 2, 3)))\n    [1, 2, 3]\n\ndefault-construct new instances;\n\n    >>> pure(F, 1)\n    F(x=1, y=1, z=1)\n\napply a function to those values;\n\n    >>> fmap(str, F(1, 2, 3))\n    F(x='1', y='2', z='3')\n\nor apply functions stored in one object to values stored in another;\n\n    >>> amap(F(str, lambda _: 999, lambda z: z + 1), F(1, 2, 3))\n    F(x='1', y=999, z=4)\n\nand gather all attributes from many instances into tuples in a new\nobject:\n\n    >>> gather(F(1, 2, 3), F(10, 11, 12), F(3, 2, 1), F(0, 0, 0))\n    F(x=(1, 10, 3, 0), y=(2, 11, 2, 0), z=(3, 12, 1, 0))\n\n[1]: [documentation](https://dataclass-applicative.readthedocs.io/en/latest/)\n",
    'author': 'Patrick Steele',
    'author_email': 'steele.pat@gmail.com',
    'maintainer': 'Patrick Steele',
    'maintainer_email': 'steele.pat@gmail.com',
    'url': 'https://github.com/prsteele/dataclass-applicative',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
