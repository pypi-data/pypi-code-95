# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['hodgepodge',
 'hodgepodge.cli',
 'hodgepodge.cli.command_groups',
 'hodgepodge.toolkits',
 'hodgepodge.toolkits.host']

package_data = \
{'': ['*']}

install_requires = \
['DAWG>=0.8.0,<0.9.0',
 'and>=0.1.1,<0.2.0',
 'antlr4-python3-runtime==4.8',
 'arrow==1.0.3',
 'certifi==2021.5.30',
 'chardet==3.0.4',
 'click>=7.0,<8.0',
 'coverage>=5.5,<6.0',
 'dacite>=1.6.0,<1.7.0',
 'python-dateutil>=2.7.3,<2.8.0',
 'python_version>=0.0.2,<0.0.3',
 'requests>=2.22.0,<2.23.0',
 'setuptools>=45.2.0,<45.3.0',
 'stix2-patterns>=1.3.2,<1.4.0',
 'stix2>=3.0.0,<3.1.0',
 'taxii2-client>=2.3.0,<2.4.0']

entry_points = \
{'console_scripts': ['hodgepodge = hodgepodge.cli:cli']}

setup_kwargs = {
    'name': 'hodgepodge',
    'version': '0.1.2',
    'description': '',
    'long_description': "# hodgepodge\n\n> _A **hodgepodge** of hopefully helpful helper code_\n\n![These are a few of my favourite functions](resources/images/a-few-of-my-favourite-things.jpg)\n\n## Features\n\n- Search for files;\n- Pack files into archives;\n- Perform pattern matching;\n- Compress and decompress objects;\n- Make the outputs from your tools more human-readable (e.g., by pretty-printing dates, file sizes, timestamps, and durations); and\n- ✨ _Way_, __*way*__, __way__ more ✨.\n\nSupported hash algorithms:\n- MD5\n- SHA-1\n- SHA-256\n- SHA-512\n\nSupported archive formats:\n- ZIP\n\nSupported compression algorithms:\n- GZIP\n\n## Installation\n\nTo install from source:\n\n```shell\n$ git clone git@github.com:whitfieldsdad/hodgepodge.git\n$ python3 setup.py install\n```\n\n## Tests\n\nYou can run the unit tests and measure code coverage at the same time as follows:\n\n```shell\n$ python3 -m tox\n...\nName                                           Stmts   Miss  Cover\n------------------------------------------------------------------\nhodgepodge/__init__.py                             0      0   100%\nhodgepodge/classes.py                             12      0   100%\nhodgepodge/cli/__init__.py                         9      1    89%\n...\nhodgepodge/types.py                               86     46    47%\nhodgepodge/uuid.py                                 3      0   100%\nhodgepodge/ux.py                                  56      6    89%\n------------------------------------------------------------------\nTOTAL                                            730    199    73%\npy3 run-test: commands[4] | /home/fishet/src/hodgepodge/.tox/py3/bin/python -m coverage html '--omit=.tox/*,tests/*'\n_______________________________________ summary _______________________________________\n  py3: commands succeeded\n  congratulations :)\n````\n\nA code coverage report will automatically be written to: `htmlcov/index.html` whenever you run `tox`.\n\nOn Linux systems, you can use `xdg-open` to open the file using the system's default web browser:\n\n```shell\n$ xdg-open htmlcov/index.html\n```\n",
    'author': 'Tyler Fisher',
    'author_email': 'tylerfisher@tylerfisher.ca',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
