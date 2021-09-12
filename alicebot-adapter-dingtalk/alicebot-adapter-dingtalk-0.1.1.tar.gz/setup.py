# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['alicebot', 'alicebot.adapter.dingtalk']

package_data = \
{'': ['*']}

install_requires = \
['alicebot>=0.2.0,<0.3.0']

setup_kwargs = {
    'name': 'alicebot-adapter-dingtalk',
    'version': '0.1.1',
    'description': 'DingTalk adapter for AliceBot.',
    'long_description': '<div align="center">\n  <a href="https://docs.alicebot.dev/"><img src="https://raw.githubusercontent.com/st1020/alicebot/master/docs/.vuepress/public/logo.png" width="200" height="200" alt="logo"></a>\n\n# AliceBot-Adapter-DingTalk\n\n**钉钉协议适配**\n\n</div>',
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
