# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dcapy',
 'dcapy.auth',
 'dcapy.cashflow',
 'dcapy.console',
 'dcapy.dca',
 'dcapy.filters',
 'dcapy.schedule',
 'dcapy.wiener']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=5.4.1,<6.0.0',
 'matplotlib>=3.3.4,<4.0.0',
 'numpy-financial>=1.0.0,<2.0.0',
 'numpy>=1.20.1,<2.0.0',
 'openpyxl>=3.0.7,<4.0.0',
 'pandas>=1.2.3,<2.0.0',
 'pyDOE2>=1.3.0,<2.0.0',
 'pydantic>=1.8.1,<2.0.0',
 'requests>=2.25.1,<3.0.0',
 'rich>=10.2.1,<11.0.0',
 'scipy>=1.6.1,<2.0.0',
 'seaborn>=0.11.1,<0.12.0',
 'statsmodels>=0.12.2,<0.13.0']

setup_kwargs = {
    'name': 'dcapy',
    'version': '0.1.6',
    'description': 'Oil and Gas DCA Workflows',
    'long_description': None,
    'author': 'Santiago Cuervo',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<4.0.0',
}


setup(**setup_kwargs)
