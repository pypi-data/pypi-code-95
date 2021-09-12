# from distutils.core import setup
#
# setup()


def readme_file():
    with open("README.rst", encoding="utf-8") as rf:
        return rf.read()


# 重新构建文本格式

from setuptools import setup

setup(name="xytestlib", version="1.0.1", description="读取README.rst文件中的内容2",
      packages=["xytestlib"], py_modules=["Tool"], author="Xy", author_email="1500671508@qq.com",
      long_description=readme_file(), url="https://github.com/wangshunzi/Python_code", license='MIT')
