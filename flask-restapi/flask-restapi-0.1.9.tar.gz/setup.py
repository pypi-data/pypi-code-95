# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['flask_restapi', 'flask_restapi.spec']

package_data = \
{'': ['*'], 'flask_restapi': ['templates/*']}

install_requires = \
['Flask[async]>=2.0.1,<3.0.0', 'PyJWT>=2.1.0,<3.0.0', 'pydantic>=1.8.2,<2.0.0']

setup_kwargs = {
    'name': 'flask-restapi',
    'version': '0.1.9',
    'description': '',
    'long_description': None,
    'author': 'jonars',
    'author_email': 'jonarsli13@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
