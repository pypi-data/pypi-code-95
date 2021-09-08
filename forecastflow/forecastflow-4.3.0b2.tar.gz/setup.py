# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['forecastflow',
 'forecastflow.api',
 'forecastflow.satellite',
 'forecastflow.satellite.google',
 'forecastflow.satellite.google.cloud',
 'forecastflow.satellite.tableau',
 'forecastflow.satellite.tableau.prep',
 'forecastflow.tabpy_support']

package_data = \
{'': ['*']}

install_requires = \
['pandas>=0.20.0', 'requests>=2.13.0', 'toml>=0.10.0']

extras_require = \
{'gcs': ['google-cloud-storage>=1.24.0'],
 'parquet': ['pyarrow>=3.0.0'],
 'tabpy': ['tabpy>=0.8.9']}

setup_kwargs = {
    'name': 'forecastflow',
    'version': '4.3.0b2',
    'description': 'ForecastFlow Python API',
    'long_description': None,
    'author': 'GRI, Inc',
    'author_email': 'forecastflow@gri.jp',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://forecastflow.jp/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6,<3.10',
}


setup(**setup_kwargs)
