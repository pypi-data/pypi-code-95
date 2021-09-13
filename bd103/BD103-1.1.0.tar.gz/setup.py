# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bd103']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'bd103',
    'version': '1.1.0',
    'description': "BD103's Python Package",
    'long_description': '# BD103 Python Package\n\nWIP, come back soon!',
    'author': 'BD103',
    'author_email': 'dont@stalk.me',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://bd103.github.io',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
