# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tablespoon']

package_data = \
{'': ['*'],
 'tablespoon': ['.pytest_cache/*',
                '.pytest_cache/v/cache/*',
                'stan/*',
                'stan/out/*']}

install_requires = \
['cmdstanpy>=0.9.77,<0.10.0',
 'numpy>=1.21.2,<2.0.0',
 'pandas>=1.3.2,<2.0.0',
 'pytest>=6.2.5,<7.0.0']

setup_kwargs = {
    'name': 'tablespoon',
    'version': '0.1.1',
    'description': 'Simple probabilistic time series benchmark models',
    'long_description': None,
    'author': 'Alex Hallam',
    'author_email': 'alexhallam6.28@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<3.11',
}


setup(**setup_kwargs)
