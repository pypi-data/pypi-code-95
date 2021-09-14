# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['viraliq']
install_requires = \
['numpy==1.19.5',
 'scikit-learn==0.24.2',
 'tensorflow>=2.6.0,<3.0.0',
 'tqdm>=4.62.2,<5.0.0']

setup_kwargs = {
    'name': 'viraliq',
    'version': '0.1.0',
    'description': 'Search for videos using an image query.',
    'long_description': None,
    'author': 'Aveek Saha',
    'author_email': 'aveek.s98@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
