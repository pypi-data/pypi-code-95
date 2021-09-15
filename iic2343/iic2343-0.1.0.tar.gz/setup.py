# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['iic2343']

package_data = \
{'': ['*']}

install_requires = \
['pyserial>=3.5,<4.0']

setup_kwargs = {
    'name': 'iic2343',
    'version': '0.1.0',
    'description': 'Write to the Basys3 directly.',
    'long_description': "# IIC2343\n\n## Installation\n\nInstall using `pip`!\n\n```sh\npip install iic2343\n```\n\n## Usage\n\nTo use the library, import the `Basys3` object directly and use the `begin`, `write` and `end` methods!\n\n```python\nfrom iic2343 import Basys3\n\ninstance = Basys3()\n\ninstance.begin(port_number=2)  # port_number is optional\ninstance.write(1, bytearray([0x00, 0x00, 0x10, 0x16, 0x01]))\ninstance.write(2, bytearray([0x00, 0x00, 0x00, 0x18, 0x03]))\ninstance.write(3, bytearray([0x00, 0x00, 0x20, 0x18, 0x03]))\ninstance.write(4, bytearray([0x00, 0x00, 0x00, 0x20, 0x00]))\ninstance.end()\n```\n\nHere, a `Basys3` instance has 3 methods:\n\n### `begin`\n\nThe method receives an optional `port_number` parameter (in needs to be an `int`). If the parameter is not present and there is only one available serial port on your machine, the `Basys3` instance will use that serial port. Otherwise, it will raise an exception. The method initializes a port to `write` to.\n\n### `write`\n\nThe method receives an `address` parameter (an `int`) and a `word` parameter (a `bytearray`). It then attempts to write the `word` on the specified `address`. If the `Basys3` instance fails, it returns a `0`. Otherwise, it returns an `int`.\n\n### `end`\n\nThe method receives no parameters, and simply closes the port initialized on the `begin` method.\n\n\n## Developing\n\nThis library uses `PyTest` as the test suite runner, and `PyLint`, `Flake8`, `Black`, `ISort` and `MyPy` as linters. It also uses `Poetry` as the default package manager.\n\nThe library includes a `Makefile` that has every command you need to start developing. If you don't have it, install `Poetry` using:\n\n```sh\nmake get-poetry\n```\n\nThen, create a virtualenv to use throughout the development process, using:\n\n```sh\nmake build-env\n```\n\nActivate the virtualenv using:\n\n```sh\n. .venv/bin/activate\n```\n\nDeactivate it using:\n\n```sh\ndeactivate\n```\n\nTo add a new package, use `Poetry`:\n\n```sh\npoetry add <new-package>\n```\n\nTo run the linters, you can use:\n\n```sh\n# The following commands auto-fix the code\nmake black!\nmake isort!\n\n# The following commands just review the code\nmake black\nmake isort\nmake flake8\nmake mypy\nmake pylint\n```\n\nTo run the tests, you can use:\n\n```sh\nmake tests\n```\n\n## Releasing\n\nTo make a new release of the library, `git switch` to the `master` branch and execute:\n\n```sh\nmake bump! minor\n```\n\nThe word `minor` can be replaced with `patch` or `major`, depending on the type of release. The `bump!` command will bump the versions of the library, create a new branch, add and commit the changes. Then, just _merge_ that branch to `master`. Finally, execute a _merge_ to the `stable` branch. Make sure to update the version before merging into `stable`, as `PyPi` will reject packages with duplicated versions.\n",
    'author': 'Daniel Leal',
    'author_email': 'dlleal@uc.cl',
    'maintainer': 'Daniel Leal',
    'maintainer_email': 'dlleal@uc.cl',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
