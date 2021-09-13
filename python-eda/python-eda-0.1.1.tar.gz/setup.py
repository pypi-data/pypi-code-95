# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['python_eda']

package_data = \
{'': ['*']}

install_requires = \
['pandas>=1.3.2,<2.0.0', 'sweetviz>=2.1.3,<3.0.0', 'typer[all]>=0.4.0,<0.5.0']

entry_points = \
{'console_scripts': ['pyeda = python_eda.main:app']}

setup_kwargs = {
    'name': 'python-eda',
    'version': '0.1.1',
    'description': 'Create a CLI wrapper for sweetviz Python exploratory data analysis (EDA) tool.',
    'long_description': '# Python EDA in CLI -- Exploratory Data Analysis in Command Line Interface\n\nThis project wraps the python exploratory data analysis tool sweetviz in a commandline interface.\n\n---\n## Usage\n\n### Generate report for a dataset\n\n`pyeda report <path-to-dataset>`\n\n### Generate report for a dataset with a target variable\n\n`pyeda target <path-to-dataset> <target-variable>`\n\n### Generate comparison report between two datasets\n\n`pyeda compare <path-to-dataset1> <path-to-dataset2>`\n\n### Generate comparison report between two datasets with a target variable\n\n`pyeda compare <path-to-dataset1> <path-to-dataset2> <target-variable>`\n\n---\n## Python EDA Illustration\nThe creation of this EDA is explained in the Towards data science post [Python Exploratory Data Analysis](https://towardsdatascience.com/how-to-do-a-ton-of-analysis-in-the-blink-of-an-eye-16fa9affce06)\n\nPackaging and distribution of this CLI EDA tool using Poetry, is explained in [You Are Not Still Using Virtualenv, Are You?](https://towardsdatascience.com/poetry-to-complement-virtualenv-44088cc78fd1)\n\nFor more interesting data science tactics please visit my [Medium profile](https://thuwarakesh.medium.com). ',
    'author': 'thuwarakeshm',
    'author_email': 'thuwarakeshm@stax.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
