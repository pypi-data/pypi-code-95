# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pylark']

package_data = \
{'': ['*']}

install_requires = \
['attrs>=21.2.0,<22.0.0', 'requests>=2.26.0,<3.0.0']

setup_kwargs = {
    'name': 'pylark',
    'version': '0.0.10',
    'description': 'Feishu/Lark Open API Python Sdk, Support ALL Open API and Event Callback.',
    'long_description': None,
    'author': 'chyroc',
    'author_email': 'chyroc@qq.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
