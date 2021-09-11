# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['contextvars_extras', 'contextvars_extras.integrations']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'contextvars-extras',
    'version': '0.0.1',
    'description': 'Contextvars made easy (WARNING: unstable alpha version. Things may break).',
    'long_description': None,
    'author': 'Dmitry Vasilyanov',
    'author_email': 'vdmit11@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7.1,<4.0.0',
}


setup(**setup_kwargs)
