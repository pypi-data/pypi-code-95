import os
from setuptools import setup

# 根据es版本安装python es库
# pymongo
# "elasticsearch-dsl>=6.3.1",
# "elasticsearch-dsl>=7.2.0",

requirements = [
    'pika',
    'numpy',
    'shortuuid',
    'threadpool',
    'redis',
    'elasticsearch_dsl',
    'matplotlib',
    'jieba',
    'wheel',
    'PyMySQL',
    'pypinyin',
    'selenium',
    'elasticsearch',
    'pymongo',
    'pandas',
    'requests',
    'beautifulsoup4',
    'sqlalchemy'
]

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='xwtools',
    version='2.0.1',
    packages=[
        "xwtools",
    ],
    license='BSD License',  # example license
    description='xwtools',
    long_description='这是一个通用的python工具包，帮助你快速的开发项目',
    install_requires=requirements,
    long_description_content_type="text/markdown",
    url='https://github.com/xulehexuwei',
    author='xuwei',
    author_email='15200813194@163.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.1',  # replace "X.Y" as appropriate
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',  # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
