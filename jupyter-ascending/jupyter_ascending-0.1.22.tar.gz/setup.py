# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['jupyter_ascending',
 'jupyter_ascending.handlers',
 'jupyter_ascending.nbextension',
 'jupyter_ascending.notebook',
 'jupyter_ascending.requests',
 'jupyter_ascending.scripts',
 'jupyter_ascending.tests']

package_data = \
{'': ['*'],
 'jupyter_ascending': ['labextension/*'],
 'jupyter_ascending.nbextension': ['static/*']}

install_requires = \
['attrs>=19.0.0',
 'edlib>=1.3.8,<2.0.0',
 'ipywidgets>=7.5.1,<8.0.0',
 'jsonrpcclient[requests]>=3.3.5,<4.0.0',
 'jsonrpcserver[requests]>=4.1.2,<5.0.0',
 'jupytext>=1.3.4,<2.0.0',
 'loguru>=0.4.1',
 'toml>=0.10.0']

setup_kwargs = {
    'name': 'jupyter-ascending',
    'version': '0.1.22',
    'description': '',
    'long_description': None,
    'author': 'Josh Albrecht',
    'author_email': 'joshalbrecht@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
