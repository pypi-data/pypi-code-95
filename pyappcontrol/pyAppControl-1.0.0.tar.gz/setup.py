# -*- coding: utf-8 -*-

import setuptools

setuptools.setup(
    name = 'pyAppControl',
    version = '1.0.0',
    author = 'Yogurt_cry',
    author_email = 'ben.2001@foxmail.com',
    description = '基于 C# 开发的客户端控制程序。用于给一些存在大量重复性的软件操作场景提供技术支持。后续会逐渐提供相应的 App 控制解决方案。仅支持 x64 位 Windows 系统',
    url = 'https://gitee.com/Yogurt_cry/pyAppControl',
    packages = setuptools.find_packages(
        include = ['pyAppControl', 'pyAppControl.*'],
    ),
    classifiers = [
        'Programming Language :: Python :: 3 :: Only',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    install_requires = [
        'pythonnet>=2.5'
    ],
    python_requires = '>=3',
    include_package_data = True,
)