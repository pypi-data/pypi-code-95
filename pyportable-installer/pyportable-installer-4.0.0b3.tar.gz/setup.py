# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyportable_installer',
 'pyportable_installer.bat_2_exe',
 'pyportable_installer.checkup',
 'pyportable_installer.compilers',
 'pyportable_installer.compilers.accessory',
 'pyportable_installer.compilers.accessory.pyportable_crypto_trial_python38.pyportable_crypto',
 'pyportable_installer.compilers.accessory.pyportable_crypto_trial_python39.pyportable_crypto',
 'pyportable_installer.main_flow',
 'pyportable_installer.main_flow.step1',
 'pyportable_installer.main_flow.step2',
 'pyportable_installer.main_flow.step3',
 'pyportable_installer.main_flow.step3.step3_1',
 'pyportable_installer.main_flow.step3.step3_2',
 'pyportable_installer.main_flow.step3.step3_3',
 'pyportable_installer.main_flow.step4']

package_data = \
{'': ['*'], 'pyportable_installer': ['template/*']}

install_requires = \
['cython',
 'embed-python-manager>=0.2.4',
 'lk-logger>=4.0.2',
 'lk-utils>=2.0.0b1',
 'pyarmor',
 'pyportable-crypto>=0.1.2']

setup_kwargs = {
    'name': 'pyportable-installer',
    'version': '4.0.0b3',
    'description': 'Build and distribute portable Python application by all-in-one configuration file.',
    'long_description': None,
    'author': 'Likianta',
    'author_email': 'likianta@foxmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
