# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['netbox_lists', 'netbox_lists.api']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'netbox-lists',
    'version': '0.2.0',
    'description': '',
    'long_description': None,
    'author': 'Devon Mar',
    'author_email': 'devonm@mdmm.ca',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
