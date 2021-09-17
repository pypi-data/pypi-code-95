# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['antlr4_grun']

package_data = \
{'': ['*']}

install_requires = \
['antlr4-python3-runtime>=4.9.2,<5.0.0', 'typer>=0.4.0,<0.5.0']

entry_points = \
{'console_scripts': ['grun = antlr4_grun.main:main']}

setup_kwargs = {
    'name': 'antlr4-grun',
    'version': '0.1.0',
    'description': 'Pure-Python replacement of `org.antlr.v4.gui.TestRig` (aka `grun`)',
    'long_description': "Pure-Python replacement of the `antlr <https://www.antlr.org/>`__ test\nrig, ``org.antlr.v4.gui.TestRig`` (aka ``grun``).\n\nThere are a few places this executable differs in the interest of better\nor more Pythonic design. For example,\n\n-  I use `click <https://click.palletsprojects.com/en/8.0.x/>`__'s\n   conventions for CLI argument parsing, which have a double-dash for\n   long-options, rather than Java's convention, which have a\n   single-dash.\n\n-  I use JSON strings to escape source lexemes. This is more elegant and\n   is easily parsed in whatever next phase of processing exists.\n",
    'author': 'Samuel Grayson',
    'author_email': 'sam@samgrayson.me',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/charmoniumQ/antlr4-python-grun',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
