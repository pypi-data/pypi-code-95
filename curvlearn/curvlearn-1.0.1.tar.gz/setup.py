# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['curvlearn', 'curvlearn.manifolds', 'curvlearn.optimizers']

package_data = \
{'': ['*']}

install_requires = \
['tensorflow>=1.15.0,<2.0.0']

setup_kwargs = {
    'name': 'curvlearn',
    'version': '1.0.1',
    'description': 'Tensorflow based non-Euclidean deep learning framework',
    'long_description': None,
    'author': 'zhirong.xzr',
    'author_email': 'zhirong.xzr@alibaba-inc.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
}


setup(**setup_kwargs)
