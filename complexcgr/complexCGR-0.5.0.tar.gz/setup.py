# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['complexcgr']

package_data = \
{'': ['*']}

install_requires = \
['Pillow>=8.3.1,<9.0.0',
 'biopython>=1.79,<2.0',
 'matplotlib>=3.4.2,<4.0.0',
 'numpy==1.19.2',
 'tqdm>=4.61.2,<5.0.0']

setup_kwargs = {
    'name': 'complexcgr',
    'version': '0.5.0',
    'description': 'complex Chaos Game Representation for DNA',
    'long_description': None,
    'author': 'Jorge Avila',
    'author_email': 'jorgeavilacartes@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
