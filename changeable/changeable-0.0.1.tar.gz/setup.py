# -*- coding: utf-8 -*-
# @Author  : LG


from setuptools import setup, find_packages

setup(
    name = "changeable",
    version = "0.0.1",
    keywords = ("pip", "changeable"),
    description = "Data transforms for object detection.",
    long_description = "Data transforms for object detection base on pytorch.",
    license = "MIT Licence",

    url = "https://github.com/yatengLG/Changeable",     #项目相关文件地址
    author = "yatengLG",
    author_email = "yatenglg@qq.com",

    packages = find_packages(),
    include_package_data = True,
    platforms = "any",
    install_requires = ["torch",
                        "numpy",
                        "pillow",
                        "opencv-python"
                        ]
)
