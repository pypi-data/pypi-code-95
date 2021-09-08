# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ykman',
 'ykman.cli',
 'ykman.hid',
 'ykman.pcsc',
 'ykman.scancodes',
 'yubikit',
 'yubikit.core']

package_data = \
{'': ['*']}

install_requires = \
['click>=6.0,<9.0',
 'cryptography>=2.1,<4.0',
 'fido2>=0.9,<1.0',
 'pyscard>=1.9,<3.0']

extras_require = \
{':python_version < "3.7"': ['dataclasses>=0.8,<0.9'],
 ':sys_platform == "win32"': ['pywin32>=223']}

entry_points = \
{'console_scripts': ['ykman = ykman.cli.__main__:main']}

setup_kwargs = {
    'name': 'yubikey-manager',
    'version': '4.0.7',
    'description': 'Tool for managing your YubiKey configuration.',
    'long_description': None,
    'author': 'Dain Nilsson',
    'author_email': 'dain@yubico.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Yubico/yubikey-manager',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
