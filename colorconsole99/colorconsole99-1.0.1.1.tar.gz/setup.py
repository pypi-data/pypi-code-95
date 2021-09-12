from setuptools import setup, find_packages

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name='colorconsole99', #　名称
    version='1.0.1.1', #　版本
    keywords='colorconsole', # 关键词
    description='A python library that displays symbols in front of command line text', # 描述
    license='MIT License', #　啥子认证哦　直接ｃｏｐｙ
    url='https://github.com/windows99-hue/colorconsole99', # 地址 可以指向自己的 开源库
    author='Kaihan Zhang 张凯涵', # 作者
    author_email='3013907412@qq.com', # 邮箱
    long_description=long_description,  # 项目的描述 读取README.md文件的信息
    long_description_content_type="text/markdown",  # 描述文档README的格式 一般md
    packages=['colorconsole99'], # 不知道
    include_package_data=True, # 不知道
    install_requires=["colorama"] # 依赖库
)
