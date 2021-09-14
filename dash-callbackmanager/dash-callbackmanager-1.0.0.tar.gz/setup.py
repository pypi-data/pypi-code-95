# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dash_callbackmanager', 'dash_callbackmanager.tests']

package_data = \
{'': ['*']}

install_requires = \
['dash<3.0.0']

setup_kwargs = {
    'name': 'dash-callbackmanager',
    'version': '1.0.0',
    'description': 'Dash callback manager, group callbacks easier within code.',
    'long_description': None,
    'author': 'Matt Seymour',
    'author_email': 'matt@enveloprisk.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/envelop-risk/dash-callbackmanager',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
