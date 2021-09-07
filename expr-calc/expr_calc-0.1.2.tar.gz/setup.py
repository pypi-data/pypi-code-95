# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['expr_calc']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'expr-calc',
    'version': '0.1.2',
    'description': 'Expression interpreter modeled after a calculator',
    'long_description': '# Calc Interpreter\n[![Python Package](https://github.com/lestherll/calc/actions/workflows/main.yml/badge.svg)](https://github.com/lestherll/calc/actions/workflows/main.yml)\n[![other branches](https://github.com/lestherll/expr_calc/actions/workflows/test_other_branch.yml/badge.svg?branch=arbitrary-precision)](https://github.com/lestherll/expr_calc/actions/workflows/test_other_branch.yml)\n[![Python Version](https://img.shields.io/pypi/pyversions/expr-calc?style=plastic)](https://pypi.org/project/expr-calc/)\n[![Python Implementation](https://img.shields.io/pypi/implementation/expr-calc?style=plastic&color=green)](https://python.org/downloads)\n\nAn interpreter modeled after a calculator implemented in Python 3.\nThe program currently only supports basic mathematical expressions.\nThe package uses Reverse Polish Notation also known as postfix expression\ninternally to easily represent mathematical expressions. This is powerful\nas it allows operators to be *organised* in such a way that precedence\nis *absolute* meaning an operator that is encountered first will always\nbe executed first.\n\nHowever, it is obvious that postfix is not *normal* or rather not usually \ntaught in schools and thus infix expression is still the way for the user \nto write expressions. The interpreter uses a modified Shunting-Yard algorithm\nto produce Abstract Syntax Trees. Evaluation of ASTs is trivial, and they are\nflexible making it easy to extend the grammar and functionality later on.\n\n## Installation\nThe package is available in PyPI and can be installed via pip.\n```shell\npip install expr-calc\n#or\npython3 -m pip install expr-calc\n```\n\n## Usage \nThe best way to run the program currently is to execute the REPL and\ncan be done in a python file or through your terminal.\n\nAssuming your present working directory is inside the cloned repo, you\ncan run the following command without the comment.\n```shell\n# inside /clone_path/expr_calc/\npython -m expr_calc\n```\nThe test suite can also be ran with `pytest` when inside the cloned repo\n```shell\npytest  # or python -m pytest\n```\n\n## Example\nOnce inside the REPL, you can start evaluating expressions. Currently, \nonly operators listed in [Features](#features) are supported.\n```shell\ncalc> 1 + 1\n2\n\ncalc> 345--500\n845\n\ncalc> -2\n-2\n\ncalc> 123 ^ 4\n228886641\n\ncalc> 32 / 1.5\n21.33333333333333333333333333\n\ncalc> 123 * 456\n56088\n\ncalc> 34 % 5\n4\n\ncalc> 4 ^ 1/2\n0.5\n\ncalc> 4 ^ (1/2)\n2.0\n```\n\n## Features\n- Infix expressions\n- Basic operators such as `+, -, *, /, %, ^`\n- Tokens created from an expression can also be fetched to be manipulated if one wanted to do so\n- Expressions are transformed into m-ary Tree objects connected to each other\n\n### Features I want to add later\n- variable support\n- custom functions\n- more mathematical functions such as `sin`, `cos`, `tan`, etc\n- and possibly a simple symbolic computation support\n\n## Resources\n- [Reverse Polish Notation](https://en.wikipedia.org/wiki/Reverse_Polish_notation)\n- [Shunting Yard Algorithm](https://en.wikipedia.org/wiki/Shunting-yard_algorithm)\n- [Floating-point arithmetic](https://floating-point-gui.de/formats/fp/)\n- [Calculator test suite](https://mozilla.github.io/calculator/test/)\n\n',
    'author': 'lestherll',
    'author_email': 'ljllacuna5@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/lestherll/expr_calc',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
