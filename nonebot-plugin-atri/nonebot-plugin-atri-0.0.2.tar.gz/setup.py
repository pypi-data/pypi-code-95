# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nonebot_plugin_atri']

package_data = \
{'': ['*'], 'nonebot_plugin_atri': ['resources/text/*', 'resources/voice/*']}

setup_kwargs = {
    'name': 'nonebot-plugin-atri',
    'version': '0.0.2',
    'description': '高い性能萝卜子',
    'long_description': None,
    'author': '风屿',
    'author_email': 'i@windis.cn',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8',
}


setup(**setup_kwargs)
