# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pytorch_axe']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.15,<2.0', 'torch>=1.6.0,<2.0.0', 'tqdm>=4.40.0,<5.0.0']

setup_kwargs = {
    'name': 'pytorch-axe',
    'version': '0.1.14',
    'description': 'Minimalist interfaces to train pytorch models with less boilerplate code',
    'long_description': None,
    'author': 'nallivam',
    'author_email': 'nallivam@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
