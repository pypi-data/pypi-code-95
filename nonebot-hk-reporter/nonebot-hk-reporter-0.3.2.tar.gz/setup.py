# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src/plugins'}

packages = \
['nonebot_hk_reporter', 'nonebot_hk_reporter.platform', 'platform']

package_data = \
{'': ['*']}

install_requires = \
['apscheduler>=3.7.0,<4.0.0',
 'bs4>=0.0.1,<0.0.2',
 'feedparser>=6.0.2,<7.0.0',
 'httpx>=0.16.1,<1.0.0',
 'nonebot-adapter-cqhttp>=2.0.0-alpha.15,<3.0.0',
 'nonebot2>=2.0.0-alpha.15,<3.0.0',
 'pillow>=8.1.0,<9.0.0',
 'pyppeteer>=0.2.5,<0.3.0',
 'tinydb>=4.3.0,<5.0.0']

setup_kwargs = {
    'name': 'nonebot-hk-reporter',
    'version': '0.3.2',
    'description': 'Subscribe message from social medias',
    'long_description': '<div align="center">\n<h1>hk-reporter </br>通用订阅推送插件</h1>\n\n\n\n[![pypi](https://badgen.net/pypi/v/nonebot-hk-reporter)](https://pypi.org/project/nonebot-hk-reporter/)\n[![felinae98](https://circleci.com/gh/felinae98/nonebot-hk-reporter.svg?style=shield)](https://circleci.com/gh/felinae98/nonebot-hk-reporter)\n[![qq group](https://img.shields.io/badge/QQ%E7%BE%A4-868610060-orange )](https://qm.qq.com/cgi-bin/qm/qr?k=pXYMGB_e8b6so3QTqgeV6lkKDtEeYE4f&jump_from=webapi)\n\n[文档](https://nonebot-hk-reporter.vercel.app)|[开发文档](https://nonebot-hk-reporter.vercel.app/dev)\n</div>\n\n## 简介\n一款自动爬取各种站点，社交平台更新动态，并将信息推送到QQ的机器人。基于 [`NoneBot2`](https://github.com/nonebot/nonebot2 ) 开发（诞生于明日方舟的蹲饼活动）\n\n\n支持的平台：\n* 微博\n    * 图片\n    * 文字\n    * 不支持视频\n    * 不支持转发的内容\n* Bilibili\n    * 图片\n    * 专栏\n    * 文字\n    * 视频链接\n    * 不支持转发的内容\n* RSS\n    * 从description中提取图片\n    * 文字\n\n\n## 功能\n* 定时爬取指定网站\n* 通过图片发送文本，防止风控\n* 使用队列限制发送频率\n\n# FAQ\n1. 报错`TypeError: \'type\' object is not subscriptable`  \n    本项目使用了Python 3.9的语法，请将Python版本升级到3.9及以上，推荐使用docker部署\n2. bot不理我  \n    请确认自己是群主或者管理员，并且检查`COMMAND_START`环境变量是否设为`[""]`\n3. 微博漏订阅了\n    微博更新了新的风控措施，某些含有某些关键词的微博会获取不到。\n\n## 鸣谢\n* [`go-cqhttp`](https://github.com/Mrs4s/go-cqhttp)：简单又完善的 cqhttp 实现\n* [`NoneBot2`](https://github.com/nonebot/nonebot2)：超好用的开发框架\n* [`HarukaBot`](https://github.com/SK-415/HarukaBot/): 借鉴了大体的实现思路\n* [`rsshub`](https://github.com/DIYgod/RSSHub)：提供了大量的api\n\n## License\nMIT\n\n',
    'author': 'felinae98',
    'author_email': 'felinae225@qq.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/felinae98/nonebot-hk-reporter',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
