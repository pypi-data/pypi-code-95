# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['alicebot', 'alicebot.adapter', 'alicebot.event', 'alicebot.plugin']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.7.0,<4.0.0', 'loguru>=0.5.0,<0.6.0', 'pydantic>=1.8.0,<1.9.0']

setup_kwargs = {
    'name': 'alicebot',
    'version': '0.2.1',
    'description': 'A simply asynchronous python chatbot framework.',
    'long_description': '<div align="center">\n  <a href="https://docs.alicebot.dev/"><img src="https://raw.githubusercontent.com/st1020/alicebot/master/docs/.vuepress/public/logo.png" width="200" height="200" alt="logo"></a>\n\n# AliceBot\n\n**简单的 Python 异步多后端机器人框架**\n\n</div>\n\n<div align="center">\n  <a href="https://raw.githubusercontent.com/st1020/alicebot/master/LICENSE">\n    <img src="https://img.shields.io/github/license/st1020/alicebot" alt="license">\n  </a>\n  <a href="https://pypi.python.org/pypi/alicebot">\n    <img src="https://img.shields.io/pypi/v/alicebot" alt="pypi">\n  </a>\n  <a href="https://pypi.python.org/pypi/alicebot">\n    <img src="https://img.shields.io/pypi/pyversions/alicebot" alt="pypi">\n  </a>\n  <a href="https://github.com/st1020/alicebot/">\n    <img src="https://img.shields.io/github/stars/st1020/alicebot?style=social" alt="github">\n  </a>\n</div>\n\n<p align="center">\n  <a href="https://docs.alicebot.dev/">文档</a>\n  ·\n  <a href="https://docs.alicebot.dev/guide/">指南</a>\n  ·\n  <a href="https://docs.alicebot.dev/guide/">API 参考</a>\n</p>\n\n## 简介\n\nAliceBot 是一个简单的 Python 异步多后端机器人框架，支持多种协议适配，可以轻松地编写易用学习和使用的插件来拓展其功能。\n\n本项目受到了 [NoneBot](https://github.com/nonebot/nonebot2/) 项目的启发，您可以在 [对比](#对比) 小节中查看这两个项目的异同，以便您选择更适合您的机器人框架。\n\n## 特点\n\nAliceBot 使用了非常灵活且易于使用的插件编写方式，您只需要编写两个方法即可实现一个功能强大的插件。\n\nAliceBot 的适配协议并不和任何一种库或网络协议绑定，您可以自由选择或编写适合您的适配器。\n\n目前 AliceBot 官方维护了以下协议适配：\n\n- [OneBot (CQHTTP) 协议](https://github.com/botuniverse/onebot) （支持QQ等）[反向 WebSocket](https://github.com/botuniverse/onebot/blob/master/v11/specs/communication/ws-reverse.md) 连接方式\n- [mirai-api-http 协议](https://github.com/project-mirai/mirai-api-http) 2.0+ [ws](https://github.com/project-mirai/mirai-api-http/blob/master/docs/adapter/WebsocketAdapter.md) 和 [reverse-ws](https://github.com/project-mirai/mirai-api-http/blob/master/docs/adapter/ReverseWebsocketAdapter.md) 连接方式\n- [钉钉](https://developers.dingtalk.com/document/robots/robot-overview) 企业机器人的outgoing（回调）连接方式\n\n更多协议正在适配中 ...\n\n## 即刻开始\n\n1. 安装：\n\n   ```bash\n   pip install alicebot\n   ```\n\n2. 第一个 AliceBot 项目：\n\n   ```python\n   from alicebot import Bot\n   \n   bot = Bot()\n   bot.load_adapter(\'alicebot.adapter.cqhttp\')\n   \n   bot.run()\n   ```\n\n3. 第一个 AliceBot 插件：\n\n   ```python\n   from alicebot.plugin import Plugin\n   \n   \n   class Echo(Plugin):\n       async def handle(self) -> None:\n           await self.event.reply(self.event.message.replace(\'echo \', \'\'))\n   \n       async def rule(self) -> bool:\n           return self.adapter.name == \'cqhttp\' and self.event.type == \'message\' and self.event.message.startswith(\'echo \')\n   ```\n\n更多信息请参阅 AliceBot [文档](https://docs.alicebot.dev/)。\n\n## 对比\n\n本项目受到了 [NoneBot](https://github.com/nonebot/nonebot2/) 项目的启发，以下介绍两者的异同。\n\n相同点：\n\n- 两者都是使用 Python 编写的，使用了协程异步的高性能机器人框架。\n- 两者都支持多种协议。\n- 两者都会对机器人收到的事件进行解析和处理，并按优先级分发给插件（事件响应器）来完成具体的功能。\n- 两者都基于 MIT 协议开源，这意味着您可以在遵循协议的前提下任意使用本项目。\n\n不同点：\n\n- 总的来说，NoneBot 是一个较为全面的机器人框架，而 AliceBot 是一个小巧简洁的机器人框架，它不包含一些复杂的高级特性，但更加灵活且易于学习（作者的观点）。\n- NoneBot 在实现上与 WebSocket 通讯协议深度绑定，它需要一个支持 ASGI 服务器协议的驱动框架，而 AliceBot 并不与任何协议绑定，它甚至可以用来驱动您的树莓派智能音箱。当然，如果您只需要一个支持常见网络聊天工具的机器人框架的话，它们并没有什么区别。\n- NoneBot 提供了很多预设规则和权限控制机制，而 AliceBot 则没有提供，由于插件编写方式的不同，AliceBot 选择给您最大的自由，您需要自行编写插件在何时运行的方法（`rule()` 方法），这在绝大部份情况下并不会造成您编写更多的代码或是影响插件的可读性，自行实现也不会非常困难，但如果您真的需要这些高级功能又不想自己实现的话，NoneBot 提供了更好的选择。\n- NoneBot 拥有相对庞大的用户基数和社区规模，也拥有数量众多的插件，而 AliceBot 则是一个新生项目，这意味着如果您使用 NoneBot 您可能会更加容易找到已经编写完毕的您感兴趣的插件，并且您当您遇到问题时也能够更快地查找到相关资料或者获得解答。\n- NoneBot 相对较为庞大，封装相对较多，完全学习理解需要一定时间，而 AliceBot 小巧简洁，封装较少，很容易掌握。\n\n总而言之，两者有着各自的特点，您可以根据需要选用。\n\n作者就是在使用 NoneBot 时觉得插件编写不是很易用，于是萌发了编写一个新的机器人框架的想法，AliceBot 就这样诞生了。\n\n## 协议与致谢\n\nAliceBot 采用 MIT 许可证开放源代码。\n\nAliceBot 的 message 模块和 cqhttp 适配器部分参考了 NoneBot 的实现，在此感谢 [NoneBot](https://github.com/nonebot/nonebot2/) 项目。',
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
