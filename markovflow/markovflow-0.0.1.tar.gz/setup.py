# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['markovflow',
 'markovflow.kernels',
 'markovflow.likelihoods',
 'markovflow.models']

package_data = \
{'': ['*']}

install_requires = \
['banded-matrices==0.0.6',
 'google-auth>=1.16.0,<2.0.0',
 'gpflow>=2.1,<3.0',
 'importlib_metadata>=1.6,<2.0',
 'numpy>=1.18.0,<2.0.0',
 'scipy>=1.4.1,<2.0.0',
 'setuptools>=41.0.0,<42.0.0',
 'tensorflow-probability==0.11.0',
 'tensorflow>2.2.0']

setup_kwargs = {
    'name': 'markovflow',
    'version': '0.0.1',
    'description': 'A Tensorflow based library for Time Series Modelling with Gaussian Processes',
    'long_description': None,
    'author': 'Markovflow Contributors',
    'author_email': 'markovflow@secondmind.ai',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>3.7,<3.8',
}


setup(**setup_kwargs)
