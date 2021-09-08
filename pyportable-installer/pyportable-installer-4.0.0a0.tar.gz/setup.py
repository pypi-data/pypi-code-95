# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyportable_installer',
 'pyportable_installer.bat_2_exe',
 'pyportable_installer.checkup',
 'pyportable_installer.compilers',
 'pyportable_installer.embed_python',
 'pyportable_installer.main_flow',
 'pyportable_installer.main_flow.step1',
 'pyportable_installer.main_flow.step2',
 'pyportable_installer.main_flow.step3',
 'pyportable_installer.main_flow.step3.step3_1',
 'pyportable_installer.main_flow.step3.step3_2',
 'pyportable_installer.main_flow.step3.step3_3',
 'pyportable_installer.main_flow.step4',
 'pyportable_installer.template.pyportable_crypto']

package_data = \
{'': ['*'],
 'pyportable_installer': ['template/*'],
 'pyportable_installer.embed_python': ['download/*']}

install_requires = \
['cython',
 'lk-logger>=4.0.0a2',
 'lk-utils>=2.0.0a0',
 'pyarmor',
 'pycryptodomex']

setup_kwargs = {
    'name': 'pyportable-installer',
    'version': '4.0.0a0',
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
