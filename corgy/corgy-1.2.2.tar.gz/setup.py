# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['corgy', 'tests']

package_data = \
{'': ['*']}

extras_require = \
{'colors': ['crayons>=0.4.0,<0.5.0']}

setup_kwargs = {
    'name': 'corgy',
    'version': '1.2.2',
    'description': 'Elegant command line parsing',
    'long_description': '# corgy\n\nElegant command line parsing for Python.\n\nCorgy allows you to create a command line interface in Python, without worrying about boilerplate code. This results in cleaner, more modular code.\n\n```python\nfrom corgy import Corgy\n\nclass ArgGroup(Corgy):\n    arg1: Annotated[Optional[int], "optional number"]\n    arg2: Annotated[bool, "a boolean"]\n\nclass MyArgs(Corgy):\n    arg1: Annotated[int, "a number"] = 1\n    arg2: Annotated[Sequence[float], "at least one float"]\n    grp1: Annotated[ArgGroup, "group 1"]\n\nargs = MyArgs.parse_from_cmdline()\n```\n\nCompare this to the equivalent code which uses argparse:\n\n```python\nfrom argparse import ArgumentParser, BooleanOptionalAction\n\nparser = ArgumentParser()\nparser.add_argument("--arg1", type=int, help="a number", default=1)\nparser.add_argument("--arg2", type=float, nargs="+", help="at least one float", required=True)\n\ngrp_parser = parser.add_argument_group("group 1")\ngrp_parser.add_argument("--grp1:arg1", type=int, help="optional number")\ngrp_parser.add_argument("--grp1:arg2", help="a boolean", action=BooleanOptionalAction)\n\nargs = parser.parse_args()\n```\n\nCorgy also provides support for more informative help messages from `argparse`, and colorized output:\n\n![Sample output from Corgy](https://raw.githubusercontent.com/jayanthkoushik/corgy/7c0b4c0ad48fb8c1838e3d31a96fdd094fd01ac6/example.svg)\n\n# Install\n**`corgy` requires Python 3.9+**. It is available on PyPI, and can be installed with pip:\n\n```bash\npip install corgy\n```\n\nSupport for colorized output requires the `crayons` package, also available on PyPI. You can pull it as a dependency for `corgy` by installing with the `colors` extra:\n\n```bash\npip install corgy[colors]\n```\n\n# Usage\nFor documentation on usage, refer to docs/index.md.\n',
    'author': 'Jayanth Koushik',
    'author_email': 'jnkoushik@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/jayanthkoushik/corgy',
    'packages': packages,
    'package_data': package_data,
    'extras_require': extras_require,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
