# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['emailtrail']

package_data = \
{'': ['*']}

install_requires = \
['dateparser>=1.0.0,<2.0.0', 'pytz>=2021.1,<2022.0']

setup_kwargs = {
    'name': 'emailtrail',
    'version': '0.4.0',
    'description': 'Analyse hops taken by an Email to reach you. Get structured information about each hop - Hostnames, Protocol used, Timestamp, and Delay',
    'long_description': None,
    'author': 'Akshay Kumar',
    'author_email': 'akshay.kmr4321@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
