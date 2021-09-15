# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['hibiapi',
 'hibiapi.api',
 'hibiapi.api.bilibili',
 'hibiapi.api.bilibili.api',
 'hibiapi.api.netease',
 'hibiapi.api.pixiv',
 'hibiapi.api.sauce',
 'hibiapi.api.tieba',
 'hibiapi.app',
 'hibiapi.app.routes',
 'hibiapi.app.routes.bilibili',
 'hibiapi.utils',
 'hibiapi.utils.decorators']

package_data = \
{'': ['*'], 'hibiapi': ['configs/*']}

install_requires = \
['aiocache[redis]>=0.11.1,<0.12.0',
 'aiofiles>=0.7.0,<0.8.0',
 'click>=8.0.1,<9.0.0',
 'confuse>=1.4.0,<2.0.0',
 'fastapi>=0.65.2,<0.66.0',
 'httpx[http2]>=0.18.0,<0.19.0',
 'loguru>=0.5.3,<0.6.0',
 'pycryptodomex>=3.10.1,<4.0.0',
 'pydantic>=1.8.2,<2.0.0',
 'python-dotenv>=0.17,<0.19',
 'python-multipart>=0.0.5,<0.0.6',
 'qrcode[pil]>=6.1,<7.0',
 'sentry-sdk>=1.1.0,<2.0.0',
 'uvicorn[standard]>=0.14.0,<0.15.0']

entry_points = \
{'console_scripts': ['hibiapi = hibiapi.__main__:main']}

setup_kwargs = {
    'name': 'hibiapi',
    'version': '0.7.4',
    'description': 'A program that implements easy-to-use APIs for a variety of commonly used sites',
    'long_description': '<!-- spell-checker: disable -->\n<!-- markdownlint-disable MD033 MD041 -->\n\n<img src=".github/logo.svg" align="right">\n\n<div align="left">\n\n# HibiAPI\n\n**_一个实现了多种常用站点的易用化API的程序._**\n\n**_A program that implements easy-to-use APIs for a variety of commonly used sites._**\n\n[![Demo Version](https://img.shields.io/badge/dynamic/json?label=demo%20status&query=%24.info.version&url=https%3A%2F%2Fapi.obfs.dev%2Fopenapi.json&style=for-the-badge&color=lightblue)](https://api.obfs.dev)\n\n![Lint](https://github.com/mixmoe/HibiAPI/workflows/Lint/badge.svg)\n![Test](https://github.com/mixmoe/HibiAPI/workflows/Test/badge.svg)\n[![Coverage](https://codecov.io/gh/mixmoe/HibiAPI/branch/main/graph/badge.svg)](https://codecov.io/gh/mixmoe/HibiAPI)\n\n![GitHub last commit](https://img.shields.io/github/last-commit/mixmoe/HibiAPI)\n[![PyPI](https://img.shields.io/pypi/v/hibiapi)](https://pypi.org/project/hibiapi/)\n[![GitHub license](https://img.shields.io/github/license/mixmoe/HibiAPI)](https://github.com/mixmoe/HibiAPI/blob/main/LICENSE)\n[![GitHub stars](https://img.shields.io/github/stars/mixmoe/HibiAPI)](https://github.com/mixmoe/HibiAPI/stargazers)\n[![GitHub forks](https://img.shields.io/github/forks/mixmoe/HibiAPI)](https://github.com/mixmoe/HibiAPI/network)\n[![GitHub issues](https://img.shields.io/github/issues/mixmoe/HibiAPI)](https://github.com/mixmoe/HibiAPI/issues)\n![Python version](https://img.shields.io/badge/python-3.8%2B-yellowgreen)\n\n</div>\n\n---\n\n## 前言\n\n- 在开发与第三方API对接的过程中, 你是否遇到了以下问题?\n  - 提供的API带有CORS跨域, 无法直接调用\n  - 调用公开数据但是需要登录凭证, 会导致登录凭证泄漏\n  - 第三方API加密实现复杂, 很难实现\n\n- 现在, 有了`HibiAPI`, 它提供多种网站公开内容的API集合, 它们包括:\n  - Pixiv的图片/小说相关信息获取和搜索\n  - Bilibili的视频/番剧等信息获取和搜索\n  - 网易云音乐的音乐/MV等信息获取和搜索\n  - 百度贴吧的帖子内容的获取\n  - and more...\n\n- 该项目的前身是 Imjad API<sup>[这是什么?](https://github.com/mixmoe/HibiAPI/wiki/FAQ#%E4%BB%80%E4%B9%88%E6%98%AFimjad-api)</sup>\n  - 由于它的使用人数过多, 致使调用超出限制, 所以本人希望提供一个开源替代来供社区进行自由的部署和使用, 从而减轻一部分该 API 的使用压力\n\n## 优势\n\n### 开源\n\n- 本项目以[Apache-2.0](https://github.com/mixmoe/HibiAPI/blob/main/LICENSE)许可开源, 这意味着你可以在**注明版权信息**的情况下进行任意使用\n\n[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2Fmixmoe%2FHibiAPI.svg?type=large)](https://app.fossa.com/projects/git%2Bgithub.com%2Fmixmoe%2FHibiAPI?ref=badge_large)\n\n### 高效\n\n- 使用 Python 的[异步机制](https://docs.python.org/zh-cn/3/library/asyncio.html), 由[FastAPI](https://fastapi.tiangolo.com/)驱动, 带来高效的使用体验 ~~虽然性能瓶颈压根不在这~~\n\n### 稳定\n\n- 在代码中大量使用[PEP-484](https://www.python.org/dev/peps/pep-0484/)引入的类型标记语法\n\n- 使用[PyLance](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance), [Flake8](https://flake8.pycqa.org/en/latest/)和[MyPy](https://mypy.readthedocs.io/)对代码进行类型推断和纠错\n\n- 不直接使用第三方 API 库, 而是全部用更加适合 Web 应用的逻辑重写第三方 API 请求, 更加可控 ~~疯狂造轮子~~\n\n## 实现进度\n\n**_[Imjad 原有 API 实现请求 (#1)](https://github.com/mixmoe/HibiAPI/issues/1)_**\n\n## 部署指南\n\n[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)\n\n- 手动部署指南: **[点击此处查看](https://github.com/mixmoe/HibiAPI/wiki/Deployment)**\n\n## 应用实例\n\n**我有更多的应用实例?** [立即 PR!](https://github.com/mixmoe/HibiAPI/pulls)\n\n- [`journey-ad/pixiv-viewer`](https://github.com/journey-ad/pixiv-viewer)\n\n  - **又一个 Pixiv 阅览工具**\n\n- 公开搭建实例\n  |    **站点名称**     |            **网址**             |        **状态**         |\n  | :-----------------: | :-----------------------------: | :---------------------: |\n  |    **官方 Demo**    |     <https://api.obfs.dev>      |  ![official][official]  |\n  |      轻零 API       |   <https://hibiapi.lite0.com>   |     ![lite0][lite0]     |\n  | Kyomotoi の菜几服务 |   <https://api.kyomotoi.moe>    |       ![kyo][kyo]       |\n  |     老狐狸 API      | <https://hibiapi.aliserver.net> | ![older-fox][older-fox] |\n\n[official]: https://img.shields.io/website?url=https%3A%2F%2Fapi.obfs.dev%2Fopenapi.json\n[lite0]: https://img.shields.io/website?url=https%3A%2F%2Fhibiapi.lite0.com%2Fopenapi.json\n[kyo]: https://img.shields.io/website?url=https%3A%2F%2Fapi.kyomotoi.moe%2Fopenapi.json\n[older-fox]: https://img.shields.io/website?url=https%3A%2F%2Fhibiapi.aliserver.net%2Fopenapi.json\n\n## 特别鸣谢\n\n[**@journey-ad**](https://github.com/journey-ad) 大佬的 [Imjad API](https://api.imjad.cn/), 是它带领我走上了编程之路\n\n### 参考项目\n\n> **正是因为有了你们, 这个项目才得以存在**\n\n- Pixiv: [`Mikubill/pixivpy-async`](https://github.com/Mikubill/pixivpy-async) [`upbit/pixivpy`](https://github.com/upbit/pixivpy)\n\n- Bilibili: [`SocialSisterYi/bilibili-API-collect`](https://github.com/SocialSisterYi/bilibili-API-collect) [`soimort/you-get`](https://github.com/soimort/you-get)\n\n- 网易云音乐: [`metowolf/NeteaseCloudMusicApi`](https://github.com/metowolf/NeteaseCloudMusicApi) [`greats3an/pyncm`](https://github.com/greats3an/pyncm) [`Binaryify/NeteaseCloudMusicApi`](https://github.com/Binaryify/NeteaseCloudMusicApi)\n\n- 百度贴吧: [`libsgh/tieba-api`](https://github.com/libsgh/tieba-api)\n\n### 贡献者们\n\n<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->\n[![All Contributors](https://img.shields.io/badge/all_contributors-6-orange.svg?style=flat-square)](#contributors-)\n<!-- ALL-CONTRIBUTORS-BADGE:END -->\n\n感谢这些为这个项目作出贡献的各位大佬:\n\n<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->\n<!-- prettier-ignore-start -->\n<!-- markdownlint-disable -->\n<table>\n  <tr>\n    <td align="center"><a href="http://kyomotoi.moe"><img src="https://avatars.githubusercontent.com/u/37587870?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Kyomotoi</b></sub></a><br /><a href="https://github.com/mixmoe/HibiAPI/commits?author=Kyomotoi" title="Documentation">📖</a> <a href="https://github.com/mixmoe/HibiAPI/commits?author=Kyomotoi" title="Tests">⚠️</a></td>\n    <td align="center"><a href="http://thdog.moe"><img src="https://avatars.githubusercontent.com/u/46120251?v=4?s=100" width="100px;" alt=""/><br /><sub><b>城倉奏</b></sub></a><br /><a href="#example-shirokurakana" title="Examples">💡</a></td>\n    <td align="center"><a href="http://skipm4.com"><img src="https://avatars.githubusercontent.com/u/40311581?v=4?s=100" width="100px;" alt=""/><br /><sub><b>SkipM4</b></sub></a><br /><a href="https://github.com/mixmoe/HibiAPI/commits?author=SkipM4" title="Documentation">📖</a></td>\n    <td align="center"><a href="https://github.com/leaf7th"><img src="https://avatars.githubusercontent.com/u/38352552?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Nook</b></sub></a><br /><a href="https://github.com/mixmoe/HibiAPI/commits?author=leaf7th" title="Code">💻</a></td>\n    <td align="center"><a href="https://github.com/jiangzhuochi"><img src="https://avatars.githubusercontent.com/u/50538375?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Jocky Chiang</b></sub></a><br /><a href="https://github.com/mixmoe/HibiAPI/commits?author=jiangzhuochi" title="Code">💻</a></td>\n    <td align="center"><a href="https://github.com/cleoold"><img src="https://avatars.githubusercontent.com/u/13920903?v=4?s=100" width="100px;" alt=""/><br /><sub><b>midori</b></sub></a><br /><a href="https://github.com/mixmoe/HibiAPI/commits?author=cleoold" title="Documentation">📖</a></td>\n  </tr>\n</table>\n\n<!-- markdownlint-restore -->\n<!-- prettier-ignore-end -->\n\n<!-- ALL-CONTRIBUTORS-LIST:END -->\n\n_本段符合 [all-contributors](https://github.com/all-contributors/all-contributors) 规范_\n',
    'author': 'mixmoe',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://api.obfs.dev',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
