# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['solace']

package_data = \
{'': ['*']}

install_requires = \
['Mako>=1.1.5,<2.0.0',
 'Werkzeug>=2.0.0,<3.0.0',
 'munch>=2.5.0,<3.0.0',
 'typer>=0.3.2,<0.4.0']

entry_points = \
{'console_scripts': ['solace = solace.main:cli']}

setup_kwargs = {
    'name': 'solace',
    'version': '0.1.8',
    'description': 'A modern microframework for building REST APIs in Python',
    'long_description': None,
    'author': 'Dan Sikes',
    'author_email': 'dansikes7@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
