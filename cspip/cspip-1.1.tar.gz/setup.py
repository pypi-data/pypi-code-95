#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   setup.py
@Time    :   2021/09/08 10:51:41
@Author  :   jixn
@Version :   1.0
'''


import setuptools
 
 
with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()
 
 
setuptools.setup(
    name='cspip',  # 模块名称
    version="1.1",  # 当前版本
    author="jixn",  # 作者
    author_email="jixn@foxmail.com",  # 作者邮箱
    description="这只是一个测试",  # 模块简介
    long_description=long_description,  # 模块详细介绍
    long_description_content_type="text/markdown",  # 模块详细介绍格式
    # url="https://github.com/zhangyafeii/timer",  # 模块github地址
    packages=setuptools.find_packages(),  # 自动找到项目中导入的模块
    # 模块相关的元数据
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    # 依赖模块
    install_requires=["requests"],
    python_requires='>=3.7',
)