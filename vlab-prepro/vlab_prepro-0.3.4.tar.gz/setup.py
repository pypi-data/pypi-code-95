# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['vlab_prepro']

package_data = \
{'': ['*']}

install_requires = \
['pandas>=1.2.4,<2.0.0', 'toolz>=0.11.1,<0.12.0']

setup_kwargs = {
    'name': 'vlab-prepro',
    'version': '0.3.4',
    'description': '',
    'long_description': None,
    'author': 'Nandan Rao',
    'author_email': 'nandanmarkrao@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
