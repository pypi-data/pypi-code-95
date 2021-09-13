# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['polyga', 'polyga.analysis']

package_data = \
{'': ['*'], 'polyga': ['default_files/dna.csv']}

install_requires = \
['SQLAlchemy>=1.4.23,<2.0.0',
 'joblib>=1.0.1,<2.0.0',
 'numpy>=1.2.4,<2.0.0',
 'pandas>=1.1,<2.0',
 'rdkit-pypi>=2021.3.3,<2022.0.0',
 'scipy>=1.7,<2.0']

setup_kwargs = {
    'name': 'polyga',
    'version': '1.0.5',
    'description': 'Polymer Genetic Algorithm',
    'long_description': None,
    'author': 'Joseph Kern',
    'author_email': 'jkern34@gatech.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Ramprasad-Group/polyga.git',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<3.10',
}


setup(**setup_kwargs)
