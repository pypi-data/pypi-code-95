from setuptools import setup

setup(
    name='sineva_edge_sdk',# 需要打包的名字,即本模块要发布的名字
    version='v1.5',#版本
    description='A  module for test', # 简要描述
    packages=["edgecom"],
    author='tower', # 作者名
    author_email='chengtao@sineva.com.cn',   # 作者邮件
    url='https://github.com/vfrtgb158/email', # 项目地址,一般是代码托管的网站
    requires=['requests','urllib3'], # 依赖包,如果没有,可以不要
    license='MIT'
)
