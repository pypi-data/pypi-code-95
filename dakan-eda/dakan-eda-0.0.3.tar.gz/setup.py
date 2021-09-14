# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['dakan_eda']

package_data = \
{'': ['*']}

install_requires = \
['google-cloud-bigquery>=2.26.0,<3.0.0']

setup_kwargs = {
    'name': 'dakan-eda',
    'version': '0.0.3',
    'description': '',
    'long_description': None,
    'author': 'vrekkebo',
    'author_email': 'vebjorn.rekkebo@nav.no',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<3.10',
}


setup(**setup_kwargs)
