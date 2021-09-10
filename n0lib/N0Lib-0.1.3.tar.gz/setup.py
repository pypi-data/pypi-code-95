#coding=utf-8
from distutils.core import setup

setup(
    name='N0Lib',
    version='0.1.3',
    license='Free',
    author='N0P3',
    author_email='n0p3@qq.com',
    description='美化CLI',
    long_description='当前是早期测试版本，部分函数未来可能会发生变化或取消且不保证与所有版本兼容。',
    py_modules=['N0Lib.graphic'],
    install_requires=[
        "cursor"
    ],
    )
#url='https://blog.n0p3.cn/2021/01/14/N0ShellAPI/',