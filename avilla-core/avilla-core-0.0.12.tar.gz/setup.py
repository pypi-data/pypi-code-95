# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['core',
 'core.builtins',
 'core.event',
 'core.execution',
 'core.message',
 'core.network',
 'core.network.clients',
 'core.network.services',
 'core.tools',
 'core.tools.filter',
 'core.tools.literature',
 'core.utilles']

package_data = \
{'': ['*']}

modules = \
['py']
install_requires = \
['aiofiles>=0.7.0,<0.8.0',
 'aiohttp>=3.7.4,<4.0.0',
 'graia-broadcast>=0.12.3,<0.13.0',
 'immutables>=0.16,<0.17',
 'pydantic>=1.8.2,<2.0.0',
 'typing-extensions>=3.10.0,<4.0.0',
 'yarl>=1.6.3,<2.0.0']

extras_require = \
{'template': ['regex>=2021.8.3,<2022.0.0']}

setup_kwargs = {
    'name': 'avilla-core',
    'version': '0.0.12',
    'description': '',
    'long_description': '<div align="center">\n\n# Avilla\n\n_The next-gen framework for IM development._ \n\n\n</div>\n\n<p align="center">\n  <a href="https://github.com/howmanybots/onebot/blob/master/README.md">\n    <img src="https://img.shields.io/badge/OneBot-v11-blue?style=flat&logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEAAAABABAMAAABYR2ztAAAAIVBMVEUAAAAAAAADAwMHBwceHh4UFBQNDQ0ZGRkoKCgvLy8iIiLWSdWYAAAAAXRSTlMAQObYZgAAAQVJREFUSMftlM0RgjAQhV+0ATYK6i1Xb+iMd0qgBEqgBEuwBOxU2QDKsjvojQPvkJ/ZL5sXkgWrFirK4MibYUdE3OR2nEpuKz1/q8CdNxNQgthZCXYVLjyoDQftaKuniHHWRnPh2GCUetR2/9HsMAXyUT4/3UHwtQT2AggSCGKeSAsFnxBIOuAggdh3AKTL7pDuCyABcMb0aQP7aM4AnAbc/wHwA5D2wDHTTe56gIIOUA/4YYV2e1sg713PXdZJAuncdZMAGkAukU9OAn40O849+0ornPwT93rphWF0mgAbauUrEOthlX8Zu7P5A6kZyKCJy75hhw1Mgr9RAUvX7A3csGqZegEdniCx30c3agAAAABJRU5ErkJggg==" alt="onebot_v11">\n  </a>\n  <img alt="PyPI" src="https://img.shields.io/pypi/v/avilla-core" />\n  <a href="https://autumn-psi.vercel.app/"><img src="https://img.shields.io/badge/docs_click here-vercel-black" /></a>\n  <img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="code_style" />\n  <img src="https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336" />\n\n</p>\n\n> "艾维莉亚(Avilla) .......希望这位楚楚可怜的少女, 能和她的血亲, 有着许多故事的少女, 在旅途中创造故事的同时, 找到她们的新的故乡."\n\n\nAvilla 被定义为 `Graia Project` 的 "下一代" 框架实现,\n通过对 [`OneBot`](https://github.com/botuniverse/onebot), [`Telegram Bot API`](https://core.telegram.org/bots) 及其他的基于不同即时通讯软件实现的各式对接接口进行总结,\n并抽象 `Relationship` 这一最为基本的模型, 构造了一个理论上可以实现零成本切换对接平台的框架.\n\n**该框架目前处于快速迭代状态, API 可能会发生 _剧烈_ 变化, 可能还不适合进行生产性的开发与运维**\n\n> 项目名称取自日本轻小说 《魔女之旅》 的角色 "艾维莉亚(Avilla)".\n\n## Roadmap\n\n - [x] `Avilla Protocol`: 对各式常见的行为进行抽象, 并通过可扩展的模型, 实现尽可能的功能可迁移性.\n    - [x] `Network API`: 统一的网络通信兼容层, 全面支持 `Client`(客户端) 与 `Service`(服务端) 的通信方式.\n    - [x] `Transformer API`: 模仿 `dart::io` 中的设计, 用于处理获得的二进制信息.\n    - [x] `Resource API`: 对含多媒体内容的消息的抽象.\n    - [ ] `Platform API`: 通过与 `Protocol` 协作, 扩展 Avilla Protocol, 使其能用于平台的特有特性.\n    - [ ] `Completed Design`: 设计并不完善, 还需要后续提供修改.\n - [x] `Avilla for OneBot`: 对  [`OneBot`](https://github.com/botuniverse/onebot) 的协议实现.\n    - [ ] `Avilla for go-cqhttp`: 对 [`go-cqhttp`](https://github.com/Mrs4s/go-cqhttp) 的扩展 API 的支持.\n - [ ] `Avilla for Telegram`: 对 [`Telegram Bot API`](https://core.telegram.org/bots) 的协议实现.\n - [ ] `Avilla for mirai-api-http`: 对 [`mirai-api-http`](https://github.com/project-mirai/mirai-api-http) 的支持.\n - And more...\n\n## 我们的愿景\n创造出比这之前还要更加具有潜力和创造性的作品, 借此有力促进社区的发展, 助力社区的艺术家们 (Developers & Artists) 创作出更加精彩的作品.\n\n## 相关项目\n<div align="center">\n\n星座的光芒是由一个个星点共同组成的, 震撼人心的作品也绝不会是一个人的功绩.  \n没有这些项目, Avilla 的实现就无从谈起.  \n排名不分顺序, 可能有许遗漏, 这里仅列出部分较为重要的项目.\n\n</div>\n\n - [`Nonebot Team`](https://github.com/nonebot):\n    - [`Nonebot v2`](https://github.com/nonebot/nonebot2): 优秀的框架, 众多灵感正来源于此.(例如 OneBot 实现的部分)\n    - [`aiocqhttp`](https://github.com/nonebot/aiocqhttp): 开发 Avilla for OneBot 时的参考实现.\n - [`Mamoe Technologies`](https://github.com/mamoe):\n    - [`mirai`](https://github.com/mamoe/mirai): The beginning, 真正做到了 "功施至今".\n    - [`mirai-api-http`](https://github.com/project-mirai/mirai-api-http): python-mirai 项目曾一直服务的对象, 个人认为尚具有极大的发展空间.\n - [`OneBot Spec`](https://github.com/botuniverse/onebot): Avilla for OneBot 所依据的实现规范, 同时也是 Avilla Protocol 设计时的参考之一.\n - [`go-cqhttp`](https://github.com/Mrs4s/go-cqhttp): 可能是现在运用最为广泛的 OneBot v11 实现.\n\n无论如何, Avilla 都是 Graia Project 下的一个子项目, 用到了其中的以下项目:\n - [`Broadcast Control`](https://github.com/GraiaProject/BroadcastControl): 事件系统实现, 最为锋利的魔剑(Magic Sword).\n\n衷心感谢这些以及其他未被提及的项目.\n\n## 开源协议\n\nAvilla 和 Avilla for OneBot, 这二者都使用 MIT 作为开源协议, 但若引用到 GPL/AGPL/LGPL 等的项目, 仍需要遵循相关规则.',
    'author': 'GreyElaina',
    'author_email': 'GreyElaina@outlook.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/GraiaProject/AvillaCore',
    'packages': packages,
    'package_data': package_data,
    'py_modules': modules,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
