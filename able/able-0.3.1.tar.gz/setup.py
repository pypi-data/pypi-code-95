# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['able', 'able.bluezdbus', 'able.corebluetooth', 'able.plugins']

package_data = \
{'': ['*']}

extras_require = \
{':sys_platform == "darwin"': ['pyobjc>=7.3,<8.0'],
 ':sys_platform == "linux"': ['dbus-next>=0.2.2,<0.3.0']}

setup_kwargs = {
    'name': 'able',
    'version': '0.3.1',
    'description': "Able stands for Allthenticate's Bluetooth Low Energy (Library) and serves to be a platform agnostic python library for communication with centrals as a BLE Peripheral.",
    'long_description': None,
    'author': 'Bernie Conrad',
    'author_email': 'bernie@allthenticate.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/allthenticate/software/able',
    'packages': packages,
    'package_data': package_data,
    'extras_require': extras_require,
    'python_requires': '>=3.6.2,<4.0',
}


setup(**setup_kwargs)
