# Author     : lin le
# CreateTime : 2021/8/31 17:13
# Email      : linle861021@163.com

import setuptools

with open("README.md", 'r') as fh:
    long_description = fh.read()
setuptools.setup(
    name="fileutil",
    version="1.0.8",
    author="linle",
    author_email="linle861021@163.com",
    description="a very very simple fileutil",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT',
    packages=setuptools.find_packages(),  # 你要安装的包，通过 setuptools.find_packages 找到当前目录下有哪些包
    include_package_data=True,  # 包含包内的数据
    python_requires='>=3.6',
    install_requires=[],  # 需要按照的依赖包
)

