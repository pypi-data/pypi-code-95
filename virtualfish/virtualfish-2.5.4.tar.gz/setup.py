# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['virtualfish', 'virtualfish.loader', 'virtualfish.test']

package_data = \
{'': ['*']}

install_requires = \
['packaging>=20.3,<21.0',
 'pkgconfig>=1.5,<2.0',
 'psutil>=5.7,<6.0',
 'virtualenv>=20,<21']

entry_points = \
{'console_scripts': ['vf = virtualfish.loader.cli:main']}

setup_kwargs = {
    'name': 'virtualfish',
    'version': '2.5.4',
    'description': 'Fish shell tool for managing Python virtual environments',
    'long_description': '# VirtualFish\n\n[![Build Status](https://img.shields.io/github/workflow/status/justinmayer/virtualfish/build)](https://github.com/justinmayer/virtualfish/actions) [![PyPI Version](https://img.shields.io/pypi/v/virtualfish)](https://pypi.org/project/virtualfish/)\n\nVirtualFish is a Python [virtual environment][Virtualenv] manager for the [Fish shell][].\n\nYou can get started by [reading the documentation][Read The Docs]. (It’s quite short… Promise!)\n\nYou can also get help on [#virtualfish on OFTC](https://webchat.oftc.net/?randomnick=1&channels=virtualfish) (`ircs://irc.oftc.net:6697/#virtualfish`), the same network as the [Fish IRC channel](https://webchat.oftc.net/?randomnick=1&channels=fish).\n\nVirtualFish is currently maintained by [Justin Mayer](https://justinmayer.com/), and was originally created by [Leigh Brenecki](https://leigh.net.au/).\n\n## A quickstart, for the impatient\n\n👉 **Fish version 3.1 or higher is required.** 👈\n\n1. `python -m pip install virtualfish`\n2. `vf install`\n3. [Add VirtualFish to your prompt](https://virtualfish.readthedocs.org/en/latest/install.html#customizing-your-fish-prompt)\n4. `vf new myvirtualenv; which python`\n\n[Read the documentation][Read The Docs] to find out more about project management, environment variable automation, auto-activation, and other plugins, as well as extending VirtualFish with events, [virtualenvwrapper][] emulation, and more.\n\n\n[Virtualenv]: https://virtualenv.pypa.io/en/latest/\n[Fish shell]: https://fishshell.com/\n[Read The Docs]: https://virtualfish.readthedocs.org/en/latest/\n[virtualenvwrapper]: https://bitbucket.org/virtualenvwrapper/virtualenvwrapper\n',
    'author': 'Justin Mayer',
    'author_email': 'entroP@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/justinmayer/virtualfish',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.2,<4.0',
}


setup(**setup_kwargs)
