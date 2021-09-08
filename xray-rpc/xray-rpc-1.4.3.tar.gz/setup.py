# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['xray_rpc',
 'xray_rpc.app.commander',
 'xray_rpc.app.dispatcher',
 'xray_rpc.app.dns',
 'xray_rpc.app.dns.fakedns',
 'xray_rpc.app.log',
 'xray_rpc.app.log.command',
 'xray_rpc.app.policy',
 'xray_rpc.app.proxyman',
 'xray_rpc.app.proxyman.command',
 'xray_rpc.app.reverse',
 'xray_rpc.app.router',
 'xray_rpc.app.router.command',
 'xray_rpc.app.stats',
 'xray_rpc.app.stats.command',
 'xray_rpc.common.log',
 'xray_rpc.common.net',
 'xray_rpc.common.protocol',
 'xray_rpc.common.serial',
 'xray_rpc.core',
 'xray_rpc.proxy.blackhole',
 'xray_rpc.proxy.dns',
 'xray_rpc.proxy.dokodemo',
 'xray_rpc.proxy.freedom',
 'xray_rpc.proxy.http',
 'xray_rpc.proxy.mtproto',
 'xray_rpc.proxy.shadowsocks',
 'xray_rpc.proxy.socks',
 'xray_rpc.proxy.trojan',
 'xray_rpc.proxy.vless',
 'xray_rpc.proxy.vless.encoding',
 'xray_rpc.proxy.vless.inbound',
 'xray_rpc.proxy.vless.outbound',
 'xray_rpc.proxy.vmess',
 'xray_rpc.proxy.vmess.inbound',
 'xray_rpc.proxy.vmess.outbound',
 'xray_rpc.transport.global',
 'xray_rpc.transport.internet',
 'xray_rpc.transport.internet.domainsocket',
 'xray_rpc.transport.internet.grpc',
 'xray_rpc.transport.internet.grpc.encoding',
 'xray_rpc.transport.internet.headers.http',
 'xray_rpc.transport.internet.headers.noop',
 'xray_rpc.transport.internet.headers.srtp',
 'xray_rpc.transport.internet.headers.tls',
 'xray_rpc.transport.internet.headers.utp',
 'xray_rpc.transport.internet.headers.wechat',
 'xray_rpc.transport.internet.headers.wireguard',
 'xray_rpc.transport.internet.http',
 'xray_rpc.transport.internet.kcp',
 'xray_rpc.transport.internet.quic',
 'xray_rpc.transport.internet.tcp',
 'xray_rpc.transport.internet.tls',
 'xray_rpc.transport.internet.udp',
 'xray_rpc.transport.internet.websocket',
 'xray_rpc.transport.internet.xtls']

package_data = \
{'': ['*']}

install_requires = \
['grpcio-tools>=1.37.0,<2.0.0',
 'grpcio>=1.37.0,<2.0.0',
 'httpx>=0.17.1,<0.18.0']

setup_kwargs = {
    'name': 'xray-rpc',
    'version': '1.4.3',
    'description': 'gRPC files generated from Xray source code.',
    'long_description': '# xray-rpc\n\n![GitHub Workflow Status](https://img.shields.io/github/workflow/status/laoshan-tech/xray-rpc/Upload%20Python%20Package?style=flat-square)\n![GitHub](https://img.shields.io/github/license/laoshan-tech/xray-rpc?style=flat-square)\n![GitHub repo size](https://img.shields.io/github/repo-size/laoshan-tech/xray-rpc?style=flat-square)\n![PyPI](https://img.shields.io/pypi/v/xray-rpc?color=blue&style=flat-square)\n[![Telegram](https://img.shields.io/badge/news-telegram-26A5E4?style=flat-square&logo=telegram)](https://t.me/laoshan_tech)\n[![Telegram](https://img.shields.io/badge/chat-telegram-26A5E4?style=flat-square&logo=telegram)](https://t.me/laoshan_tech_discuss)\n\n通过 Xray 源码 proto 文件自动生成的 gRPC 代码，版本号对应 Xray 相对应。\n\n## 安装\n\n通过 pip 安装。\n\n```shell\npip install xray-rpc\n```\n\n## 使用\n\n参考 [xray-node](https://github.com/laoshan-tech/xray-node/blob/master/xray_node/core/xray.py) 中的用法。',
    'author': 'laoshan-taoist',
    'author_email': '65347330+laoshan-taoist@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/laoshan-tech/xray-rpc',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
