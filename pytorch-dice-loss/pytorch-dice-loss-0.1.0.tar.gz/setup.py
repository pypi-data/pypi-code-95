# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pytorch_dice_loss']

package_data = \
{'': ['*']}

install_requires = \
['einops>=0.3.2,<0.4.0', 'torch>=1.9.0,<2.0.0']

setup_kwargs = {
    'name': 'pytorch-dice-loss',
    'version': '0.1.0',
    'description': 'Dice Loss in PyTorch for NLP',
    'long_description': None,
    'author': 'Chenghao Mou',
    'author_email': 'mouchenghao@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
