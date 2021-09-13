# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': '.'}

packages = \
['textalytics_aws',
 'textalytics_azure',
 'textalytics_gcp',
 'textalytics_hosted']

package_data = \
{'': ['*']}

install_requires = \
['azure-ai-textanalytics>=5.1.0,<6.0.0',
 'boto3>=1.18.40,<2.0.0',
 'google-cloud-language>=2.2.2,<3.0.0',
 'pydantic>=1.8.2,<2.0.0',
 'textalytics-core>=0.1.1,<0.2.0',
 'textalytics-python-client>=0.1.0,<0.2.0']

entry_points = \
{'console_scripts': ['test = scripts:test']}

setup_kwargs = {
    'name': 'textalytics-cloud-api-adapters',
    'version': '0.1.3',
    'description': 'textalytics adapters for various cloud apis',
    'long_description': None,
    'author': 'Manoj Bharadwaj',
    'author_email': 'manoj@cloudcosmos.tech',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
