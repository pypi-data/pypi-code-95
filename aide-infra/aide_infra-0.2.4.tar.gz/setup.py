# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aide', 'aide.messaging', 'aide.pacs_client']

package_data = \
{'': ['*']}

install_requires = \
['pika>=1.2.0,<2.0.0', 'pydicom>=2.1.2,<3.0.0', 'pynetdicom>=1.5.7,<2.0.0']

setup_kwargs = {
    'name': 'aide-infra',
    'version': '0.2.4',
    'description': '',
    'long_description': None,
    'author': 'Josh Liberty',
    'author_email': 'josh.liberty@answerdigital.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
