# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pgmax', 'pgmax.bp', 'pgmax.fg']

package_data = \
{'': ['*']}

install_requires = \
['jax>=0.2.14,<0.3.0',
 'jaxlib>=0.1.67,<0.2.0',
 'jupyter>=1.0.0,<2.0.0',
 'matplotlib>=3.4.2,<4.0.0',
 'numpy>=1.20.3,<2.0.0',
 'scipy>=1.6.3,<2.0.0']

setup_kwargs = {
    'name': 'pgmax',
    'version': '0.2.0',
    'description': 'Loopy belief propagation for factor graphs on discrete variables, in JAX!',
    'long_description': "[![continuous-integration](https://github.com/vicariousinc/PGMax/actions/workflows/ci.yaml/badge.svg)](https://github.com/vicariousinc/PGMax/actions/workflows/ci.yaml)\n[![PyPI version](https://badge.fury.io/py/pgmax.svg)](https://badge.fury.io/py/pgmax)\n\n# PGMax\nPGMax is a library for working with Factor Graphs in [JAX](https://jax.readthedocs.io/en/latest/). It currently provides an interface for specifying factor graphs of any type, as well as an efficient implementation of max-product belief propagation and inference on these graphs.\n\n## Installation Instructions\n### User\n1. Install the library using pip via: `pip install pgmax`\n1. By default this installs JAX for CPU. If you'd like to use JAX with a GPU and specific CUDA version (highly recommended), follow the official instructions [here](https://github.com/google/jax#pip-installation-gpu-cuda).\n\n### Developer\n1. Clone this project's [GitHub Repository](https://github.com/vicariousinc/PGMax)\n1. Install Poetry by following [these instructions](https://python-poetry.org/docs/master/). Note: you may need to logout and log back in after running the install command for the `poetry --version` command to work in your shell environment.\n1. Navigate to this project's directory and activate a poetry shell via the command `poetry shell`. This creates and activates a virtual environment for you to use with this project.\n1. Install the project's dependencies into your virtual environment with the command `poetry install`. Your environment will now contain both developer and user dependencies!\n    1. By default this installs JAX for CPU. If you'd like to use JAX with a GPU and specific CUDA version (highly recommended), follow the official instructions [here](https://github.com/google/jax#pip-installation-gpu-cuda).\n1. Do `pre-commit install` to initialize pre-commit hooks",
    'author': 'Nishanth Kumar',
    'author_email': 'nkumar@vicarious.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/vicariousinc/PGMax',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<3.8',
}


setup(**setup_kwargs)
