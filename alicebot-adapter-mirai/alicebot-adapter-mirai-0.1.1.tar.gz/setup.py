# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['alicebot', 'alicebot.adapter.mirai', 'alicebot.adapter.mirai.event']

package_data = \
{'': ['*']}

install_requires = \
['alicebot>=0.2.0,<0.3.0']

setup_kwargs = {
    'name': 'alicebot-adapter-mirai',
    'version': '0.1.1',
    'description': 'Mirai adapter for AliceBot.',
    'long_description': '<div align="center">\n  <a href="https://docs.alicebot.dev/"><img src="https://raw.githubusercontent.com/st1020/alicebot/master/docs/.vuepress/public/logo.png" width="200" height="200" alt="logo"></a>\n\n# AliceBot-Adapter-CQHTTP\n\n**Mirai 协议适配**\n\n</div>',
    'author': 'st1020',
    'author_email': 'stone_1020@qq.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://docs.alicebot.dev/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
