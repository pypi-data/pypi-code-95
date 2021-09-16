# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['iic2343', 'iic2343.cli']

package_data = \
{'': ['*']}

install_requires = \
['pyserial>=3.5,<4.0']

entry_points = \
{'console_scripts': ['iic2343 = iic2343.cli.core:dispatcher']}

setup_kwargs = {
    'name': 'iic2343',
    'version': '0.2.0',
    'description': 'Write to the Basys3 ROM directly.',
    'long_description': '<h1 align="center">IIC2343</h1>\n\n<p align="center">\n    <em>\n        Write to the Basys3 ROM directly.\n    </em>\n</p>\n\n<p align="center">\n<a href="https://pypi.org/project/iic2343" target="_blank">\n    <img src="https://img.shields.io/pypi/v/iic2343?label=version&logo=python&logoColor=%23fff&color=306998" alt="PyPI - Version">\n</a>\n\n<a href="https://github.com/daleal/iic2343/actions?query=workflow%3Atests" target="_blank">\n    <img src="https://img.shields.io/github/workflow/status/daleal/iic2343/tests?label=tests&logo=python&logoColor=%23fff" alt="Tests">\n</a>\n\n<a href="https://codecov.io/gh/daleal/iic2343" target="_blank">\n    <img src="https://img.shields.io/codecov/c/gh/daleal/iic2343?label=coverage&logo=codecov&logoColor=ffffff" alt="Coverage">\n</a>\n\n<a href="https://github.com/daleal/iic2343/actions?query=workflow%3Alinters" target="_blank">\n    <img src="https://img.shields.io/github/workflow/status/daleal/iic2343/linters?label=linters&logo=github" alt="Linters">\n</a>\n</p>\n\n## Installation\n\nInstall using `pip`!\n\n```sh\n$ pip install iic2343\n```\n\n## Usage\n\nTo use the library, import the `Basys3` object directly and use the `begin`, `write` and `end` methods!\n\n```python\nfrom iic2343 import Basys3\n\ninstance = Basys3()\n\ninstance.begin(port_number=2)  # port_number is optional\ninstance.write(1, bytearray([0x00, 0x00, 0x10, 0x16, 0x01]))\ninstance.write(2, bytearray([0x00, 0x00, 0x00, 0x18, 0x03]))\ninstance.write(3, bytearray([0x00, 0x00, 0x20, 0x18, 0x03]))\ninstance.write(4, bytearray([0x00, 0x00, 0x00, 0x20, 0x00]))\ninstance.end()\n```\n\n### Methods\n\nHere, a `Basys3` instance has 3 methods:\n\n#### `begin`\n\nThe method receives an optional `port_number` parameter (in needs to be an `int`). If the parameter is not present and there is only one available serial port on your machine, the `Basys3` instance will use that serial port. Otherwise, it will raise an exception. The method initializes a port to `write` to.\n\n#### `write`\n\nThe method receives an `address` parameter (an `int`) and a `word` parameter (a `bytearray`). It then attempts to write the `word` on the specified `address`. If the `Basys3` instance fails, it returns a `0`. Otherwise, it returns an `int`.\n\n#### `end`\n\nThe method receives no parameters, and simply closes the port initialized on the `begin` method.\n\n### Attributes\n\nThe `Basys3` instance also has 1 attribute:\n\n#### `available_ports`\n\nThis attribute has a list with all the available ports (the ports are [`ListPortInfo`](https://pythonhosted.org/pyserial/tools.html#serial.tools.list_ports.ListPortInfo) objects). You don\'t **need** to use this attribute, but it might come in handy if you want to generate a GUI for your users or something like that.\n\n## CLI\n\nThis module also includes a CLI! It is quite simple, but it might be useful to see ports on your machine. The CLI works as follows:\n\n```sh\n$ iic2343 --help\nusage: iic2343 [-h] [-v] {ports} ...\n\nCommand line interface tool for iic2343.\n\npositional arguments:\n  {ports}        Action to be executed.\n\noptional arguments:\n  -h, --help     show this help message and exit\n  -v, --version  show program\'s version number and exit\n```\n\nThat was the `--help` flag. Use it when you\'re not sure how something works! To see a list of your available ports, run the following command on your terminal:\n\n```sh\n$ iic2343 ports\n(0) ttyS0\n      desc: ttyS0\n(1) ttyUSB0\n      desc: n/a\n(2) ttyUSB1\n      desc: CP2102 USB to UART Bridge Controller\n3 ports found\n```\n\nYou can also use the `--verbose` flag to get a bit more information about each port:\n\n```sh\n$ iic2343 ports --verbose\n(0) /dev/ttyS0\n      desc: ttyS0\n      hwid: PNP0501\n(1) /dev/ttyUSB0\n      desc: n/a\n      hwid: PNP0502\n(2) /dev/ttyUSB1\n      desc: CP2102 USB to UART Bridge Controller\n      hwid: USB VID:PID=10C4:EA60 SER=0001 LOCATION=2-1.6\n3 ports found\n```\n\n## Developing\n\nThis library uses `PyTest` as the test suite runner, and `PyLint`, `Flake8`, `Black`, `ISort` and `MyPy` as linters. It also uses `Poetry` as the default package manager.\n\nThe library includes a `Makefile` that has every command you need to start developing. If you don\'t have it, install `Poetry` using:\n\n```sh\nmake get-poetry\n```\n\nThen, create a virtualenv to use throughout the development process, using:\n\n```sh\nmake build-env\n```\n\nActivate the virtualenv using:\n\n```sh\n. .venv/bin/activate\n```\n\nDeactivate it using:\n\n```sh\ndeactivate\n```\n\nTo add a new package, use `Poetry`:\n\n```sh\npoetry add <new-package>\n```\n\nTo run the linters, you can use:\n\n```sh\n# The following commands auto-fix the code\nmake black!\nmake isort!\n\n# The following commands just review the code\nmake black\nmake isort\nmake flake8\nmake mypy\nmake pylint\n```\n\nTo run the tests, you can use:\n\n```sh\nmake tests\n```\n\n## Releasing\n\nTo make a new release of the library, `git switch` to the `master` branch and execute:\n\n```sh\nmake bump! minor\n```\n\nThe word `minor` can be replaced with `patch` or `major`, depending on the type of release. The `bump!` command will bump the versions of the library, create a new branch, add and commit the changes. Then, just _merge_ that branch to `master`. Finally, execute a _merge_ to the `stable` branch. Make sure to update the version before merging into `stable`, as `PyPi` will reject packages with duplicated versions.\n',
    'author': 'Daniel Leal',
    'author_email': 'dlleal@uc.cl',
    'maintainer': 'Daniel Leal',
    'maintainer_email': 'dlleal@uc.cl',
    'url': 'https://github.com/daleal/iic2343',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
