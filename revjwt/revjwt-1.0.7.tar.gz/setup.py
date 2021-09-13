# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['revjwt']

package_data = \
{'': ['*']}

install_requires = \
['PyJWT>=2.0.0,<3.0.0',
 'boto3>=1.17.27,<2.0.0',
 'jwcrypto>=0.8,<0.9',
 'requests>=2.25.1,<3.0.0']

setup_kwargs = {
    'name': 'revjwt',
    'version': '1.0.7',
    'description': '',
    'long_description': None,
    'author': 'Chien',
    'author_email': 'a0186163@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
