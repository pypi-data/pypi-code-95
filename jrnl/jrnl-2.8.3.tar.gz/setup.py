# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['jrnl', 'jrnl.plugins']

package_data = \
{'': ['*'], 'jrnl': ['templates/*']}

install_requires = \
['ansiwrap>=0.8.4,<0.9.0',
 'asteval>=0.9,<0.10',
 'colorama>=0.4',
 'cryptography>=3.0',
 'keyring>=21.0',
 'parsedatetime>=2.6',
 'python-dateutil>=2.8,<3.0',
 'pytz>=2020',
 'pyxdg>=0.27.0',
 'pyyaml>=5.1',
 'tzlocal>2.0,<3.0']

extras_require = \
{'testing': ['behave>=1.2,<2.0',
             'pytest>=6.2',
             'pytest-bdd>=4.0.1',
             'toml>=0.10']}

entry_points = \
{'console_scripts': ['jrnl = jrnl.cli:cli']}

setup_kwargs = {
    'name': 'jrnl',
    'version': '2.8.3',
    'description': 'Collect your thoughts and notes without leaving the command line.',
    'long_description': '<p align="center">\n<a href="https://jrnl.sh">\n<img align="center" src="https://github.com/jrnl-org/jrnl/blob/develop/docs_theme/assets/readme-header.png"/>\n</a>\n</p>\n\njrnl\n [![Testing](https://github.com/jrnl-org/jrnl/workflows/Testing/badge.svg)](https://github.com/jrnl-org/jrnl/actions?query=workflow%3ATesting)\n [![Downloads](https://pepy.tech/badge/jrnl)](https://pepy.tech/project/jrnl)\n [![Version](http://img.shields.io/pypi/v/jrnl.svg?style=flat)](https://pypi.python.org/pypi/jrnl/)\n [![Homebrew](https://img.shields.io/homebrew/v/jrnl?style=flat-square)](https://formulae.brew.sh/formula/jrnl)\n [![Gitter](https://img.shields.io/gitter/room/jrnl-org/jrnl)](https://gitter.im/jrnl-org/jrnl)\n====\n\n_To get help, [submit an issue](https://github.com/jrnl-org/jrnl/issues/new/choose) on\nGithub._\n\n`jrnl` is a simple journal application for the command line.\n\nYou can use it to easily create, search, and view journal entries. Journals are\nstored as human-readable plain text, and can also be encrypted using  [AES\nencryption](http://en.wikipedia.org/wiki/Advanced_Encryption_Standard).\n\n## In a Nutshell\n\nTo make a new entry, just enter\n\n``` sh\njrnl yesterday: Called in sick. Used the time to clean the house and write my\nbook.\n```\n\n`yesterday:` is  interpreted by `jrnl` as a timestamp. Everything until the\nfirst sentence ending (either `.`, `?`, or `!`) is interpreted as the title, and\nthe rest as the body. In your journal file, the result will look like this:\n\n    [2012-03-29 09:00] Called in sick.\n    Used the time to clean the house and write my book.\n\nIf you just call `jrnl`, you will be prompted to compose your entry - but you\ncan also configure _jrnl_ to use your external editor.\n\nFor more information, please read the\n[documentation](https://jrnl.sh).\n\n## Contributors\n\n### Maintainers\n\nOur maintainers help keep the lights on for the project:\n\n * Jonathan Wren ([wren](https://github.com/wren))\n * Micah Ellison ([micahellison](https://github.com/micahellison))\n\nPlease thank them if you like `jrnl`!\n\n### Code Contributors\n\nThis project is made with love by the many fabulous people who have contributed.\n`jrnl` couldn\'t exist without each and every one of you!\n\n<a href="https://github.com/jrnl-org/jrnl/graphs/contributors"><img\nsrc="https://opencollective.com/jrnl/contributors.svg?width=890&button=false"\n/></a>\n\nIf you\'d also like to help make `jrnl` better, please see our [contributing\ndocumentation](CONTRIBUTING.md).\n\n### Financial Backers\n\nAnother way show support is through direct financial contributions. These funds\ngo to covering our costs, and are a quick way to show your appreciation for\n`jrnl`.\n\n[Become a financial contributor](https://opencollective.com/jrnl/contribute)\nand help us sustain our community.\n\n<a href="https://opencollective.com/jrnl"><img\nsrc="https://opencollective.com/jrnl/individuals.svg?width=890"></a>\n',
    'author': 'jrnl contributors',
    'author_email': 'jrnl-sh@googlegroups.com',
    'maintainer': 'Jonathan Wren and Micah Ellison',
    'maintainer_email': 'jrnl-sh@googlegroups.com',
    'url': 'https://jrnl.sh',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7.0,<3.11',
}


setup(**setup_kwargs)
