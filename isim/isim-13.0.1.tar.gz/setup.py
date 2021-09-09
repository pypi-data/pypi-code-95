# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['isim']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'isim',
    'version': '13.0.1',
    'description': 'Python wrapper around the simctl utility',
    'long_description': '# isim\n\n![Python Version](https://img.shields.io/pypi/pyversions/isim.svg) ![Xcode 11.0](https://img.shields.io/badge/Xcode-11.0-blue.svg) \n\nThis is a Python wrapper around the `xcrun simctl` utility that Apple provides for interacting with the various Xcode developer tools. \n\n`xcrun simctl` is the tool for interacting with the iOS simulator and is the main focus of this module. The syntax is designed to remain as close to that which would be used on the command line as possible. For example, to list all runtimes on the command line you would do:\n\n    xcrun simctl list runtimes\n\nWith this module you can simply do:\n\n    from isim import Runtime\n    print(Runtime.list_all())\n\nMost functions are on the item that they affect. So instead of running something on a device like:\n\n    xcrun simctl do_thing <DEVICE_ID> arg1 arg2 ...\n\nYou can do this:\n\n    from isim import Device\n    iPhone7 = Device.from_name("iPhone 7")\n    iPhone7.do_thing(arg1, arg2, ...)\n\n## Testing\n\nTo run the tests, all you need to do is run `python -m pytest tests` from the root directory.\n\n## isim and Xcode Versioning\n\n`isim` follows the current supported version of Xcode for its version scheme. \n\nFor example, if the currently supported version of Xcode is 11, then isim will be versioned as `11.minor.patch`. The `minor` version will only be increased if there is a breaking change in Xcode requiring it (which is unlikely). The patch version will be increased with each patch that is made.\n\nThere is no expectation of backwards compatibility. If you need to support an older version of Xcode, you\'ll almost always need an older major version. \n\n_Note:_ The Xcode developer tools are installed with new betas. That means that if you are running Xcode 10.2.1, but then install the Xcode 11 beta, the simulator tools will be for Xcode 11, rather than Xcode 10, even if you run `xcode-select -s`. That means that as soon as you install a beta on your machine, you will need to use that version of isim. \n',
    'author': 'Dale Myers',
    'author_email': 'dale@myers.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/dalemyers/xcrun',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
