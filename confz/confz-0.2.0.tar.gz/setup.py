# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['confz', 'confz.loaders']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=5.4.1,<6.0.0', 'pydantic>=1.8.2,<2.0.0']

setup_kwargs = {
    'name': 'confz',
    'version': '0.2.0',
    'description': '',
    'long_description': None,
    'author': 'Silvan Melchior',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
