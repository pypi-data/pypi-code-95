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
    'version': '0.0.10',
    'description': 'EDA data for dakan',
    'long_description': '# dakan-eda\n\nThis package is meant to extract privacy conserving EDA-data from a BigQuery table to a viewer in Datakatalogen.\n',
    'author': 'vrekkebo',
    'author_email': 'vebjorn.rekkebo@nav.no',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/navikt/dakan-eda',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<3.10',
}


setup(**setup_kwargs)
