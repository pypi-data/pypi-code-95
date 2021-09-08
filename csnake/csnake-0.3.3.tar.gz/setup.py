# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['csnake']

package_data = \
{'': ['*']}

extras_require = \
{'numpy': ['numpy>=1.17'], 'pillow': ['pillow>=6.1'], 'sympy': ['sympy>=1.4']}

setup_kwargs = {
    'name': 'csnake',
    'version': '0.3.3',
    'description': 'C code generation helper package.',
    'long_description': '######\ncsnake\n######\n\n.. image:: https://gitlab.com/andrejr/csnake/badges/master/pipeline.svg\n   :alt: pipeline status\n   :target: https://gitlab.com/andrejr/csnake/pipelines\n.. image:: https://gitlab.com/andrejr/csnake/badges/master/coverage.svg\n   :alt: coverage report\n   :target: https://andrejr.gitlab.io/csnake/coverage/index.html\n\nCsnake is a Python 3 package that helps you generate C code from Python.\n\nCsnake provides you with a consistent and opinionated API that helps you\nstructure your C-generating Python code.\nIt does so by providing classes and functions for generating every C language\nconstruct.\n\nProbably the most important feature is the ability to initialize a value to\n``struct`` and *array* initializers from Python *dicts* and *lists* (actually,\n``Map``\\s and ``Collection``\\s), nested arbitrarily.\n\nHere\'s a taste:\n\n.. code-block:: python\n\n   from csnake import CodeWriter, Variable, FormattedLiteral\n   import numpy as np\n\n   var = Variable(\n       "test",\n       primitive="struct whatever",\n       value={\n           "field1": [{"x": num, "y": 10 - num} for num in range(2)],\n           "field2": {"test": range(3), "field": np.arange(6).reshape(2, 3)},\n           "field3": FormattedLiteral([30, 31, 32], int_formatter=hex),\n           "field4": 8,\n       },\n   )\n   cw = CodeWriter()\n   cw.add_variable_initialization(var)\n   print(cw)\n\n\nThis yields:\n\n.. code-block:: c\n\n    struct whatever test = {\n        .field1 = {\n            {\n                .x = 0,\n                .y = 10\n            },{\n                .x = 1,\n                .y = 9\n            }\n        },\n        .field2 = {\n            .test = {0, 1, 2},\n            .field = {\n                {0, 1, 2},\n                {3, 4, 5}\n            }\n\n        },\n        .field3 = {0x1e, 0x1f, 0x20},\n        .field4 = 8\n    };\n\nAs shown, ``numpy`` arrays are supported as values (so are ``sympy`` arrays),\nand values can be formatted by arbitrary functions (here we\'re using ``hex`` to\noutput ints as hex literals for member `field3`).\n\nMotivation\n==========\n\nCsnake\'s varable generation was motivated by a common embedded development\ntask: inputting data into C code.\n\nCsnake should be of help when generating C code for representing data like\nbitmaps, fonts, statemachines, lookup tables - as arrays and structs.\nIt can also be used for loop unrolling, templating, ...\n\nCsnake  can be easily incorporated into a build system (Make, CMake,\nScons,...), and also goes along great with Jinja2 and\n`Ned Batchelder\'s cog <https://nedbatchelder.com/code/cog/>`_.\n\nDocumentation\n=============\n\nDocumentation (Sphinx) can be viewed on\n`GitLab pages for this package <https://andrejr.gitlab.io/csnake/>`_.\n\nExamples\n========\n\nCsnake is used on several of my yet-to-be-released open source embedded\nprojects. I\'ll be adding those (and other) examples along the way.\n\nCredits\n=======\n\nCsnake is a major re-implementation (and improvement) of\n`C-Snake <https://github.com/SchrodingersGat/C-Snake>`_\nby\n`Oliver <https://github.com/SchrodingersGat>`_\n(original idea) and Andrej (variable initialization idea and implementation,\nauthor of this package).\n\nIt\'s provided under the MIT license.\n\nChangelog\n=========\n\nThe changelog can be found within the documentation, \n`here <https://andrejr.gitlab.io/csnake/changes.html>`_.\n',
    'author': 'Andrej Radović',
    'author_email': 'r.andrej@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/andrejr/csnake',
    'packages': packages,
    'package_data': package_data,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<3.11',
}


setup(**setup_kwargs)
