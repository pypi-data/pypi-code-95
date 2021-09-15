# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['vps_network',
 'vps_network.vps_api',
 'vps_network.vps_php',
 'vps_network.vps_ping',
 'vps_network.vps_quick',
 'vps_network.vps_speed',
 'vps_network.vps_trace',
 'vps_network.vps_utils']

package_data = \
{'': ['*']}

install_requires = \
['click>=8,<9',
 'icmplib>=3.0,<4',
 'pydantic>=1.7,<2.0',
 'requests>=2.25,<3',
 'rich>=10,<11',
 'speedtest-cli>=2.1,<3']

setup_kwargs = {
    'name': 'vps-network',
    'version': '0.6.0',
    'description': 'VPS Network Speed Test',
    'long_description': '# VPS 网络测试工具\n\n![pytest](https://github.com/QiYuTechDev/vps_network/workflows/pytest/badge.svg)\n![Pylama Lint](https://github.com/QiYuTechDev/vps_network/workflows/Pylama%20Lint/badge.svg)\n![CodeQL](https://github.com/QiYuTechDev/vps_network/workflows/CodeQL/badge.svg)\n![Black Code Format Check](https://github.com/QiYuTechDev/vps_network/workflows/Black%20Code%20Format%20Check/badge.svg)\n![docker build](https://github.com/QiYuTechDev/vps_network/workflows/docker%20build/badge.svg)\n![docker release](https://github.com/QiYuTechDev/vps_network/workflows/docker%20release/badge.svg)\n[![CodeFactor](https://www.codefactor.io/repository/github/qiyutechdev/vps_network/badge)](https://www.codefactor.io/repository/github/qiyutechdev/vps_network)\n\n网络速度测试工具箱\n\n## 文档 & 博客\n\n* [文档](https://oss.qiyutech.tech/vps_bench/index.html)\n* [发布记录](https://blog.qiyutech.tech/202102/28_bench_tool/)\n',
    'author': 'dev',
    'author_email': 'dev@qiyutech.tech',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://vps.qiyutech.tech/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
