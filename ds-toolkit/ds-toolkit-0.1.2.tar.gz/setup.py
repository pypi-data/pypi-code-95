# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ds_toolkit']

package_data = \
{'': ['*']}

install_requires = \
['PyPrind>=2.11.3,<3.0.0',
 'bs4>=0.0.1,<0.0.2',
 'python-magic>=0.4.24,<0.5.0',
 'requests>=2.26.0,<3.0.0']

setup_kwargs = {
    'name': 'ds-toolkit',
    'version': '0.1.2',
    'description': 'A toolkit full of random & helpful abilities',
    'long_description': '# ds-toolkit\n\nBasic toolkit for developing with Python.\n\nSome capabilities include:\n- Reading files\n- Download files from the internet\n- Scraping a webpage for downloadable files\n- Unzipping & zipping files\n- Reading & writing JSON files\n- Progress bar for iteration (generated from PyPrind)\n',
    'author': 'David Silva',
    'author_email': 'davidsilva2841+gitlab@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/davidsilva2841/ds-toolkit',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
