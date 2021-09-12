# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pypette']

package_data = \
{'': ['*']}

install_requires = \
['Sphinx>=4.1.2,<5.0.0',
 'crayons>=0.4.0,<0.5.0',
 'sphinx-autobuild>=2021.3.14,<2022.0.0']

setup_kwargs = {
    'name': 'pypette',
    'version': '0.0.10',
    'description': 'pypette (to be read as pipette) is a module which makes building pipelines ridiculously simple, allowing users to control the flow with minimal instructions.',
    'long_description': None,
    'author': 'csurfer',
    'author_email': 'sharma.vishwas88@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
