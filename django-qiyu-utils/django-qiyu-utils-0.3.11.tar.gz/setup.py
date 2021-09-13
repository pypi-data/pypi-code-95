# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['django_qiyu_utils', 'django_qiyu_utils.div_node']

package_data = \
{'': ['*']}

install_requires = \
['django>=3.1,<3.3']

setup_kwargs = {
    'name': 'django-qiyu-utils',
    'version': '0.3.11',
    'description': 'Django 辅助工具类',
    'long_description': '# 奇遇科技 Django 辅助工具箱\n\n![PyPI - Version](https://img.shields.io/pypi/v/django-qiyu-utils)\n![PyPI - Python Version](https://img.shields.io/pypi/pyversions/django-qiyu-utils)\n![PyPI - Downloads](https://img.shields.io/pypi/dm/django-qiyu-utils)\n![PyPI - Wheel](https://img.shields.io/pypi/wheel/django-qiyu-utils)\n![GitHub repo size](https://img.shields.io/github/repo-size/qiyutechdev/django-qiyu-utils)\n![Lines of code](https://img.shields.io/tokei/lines/github/qiyutechdev/django-qiyu-utils)\n\n## 警告\n\n    这些代码为内部使用\n\n## WARNING\n\n    USE IT AT YOUR OWN RISK!!\n',
    'author': 'dev',
    'author_email': 'dev@qiyutech.tech',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://oss.qiyutech.tech/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
