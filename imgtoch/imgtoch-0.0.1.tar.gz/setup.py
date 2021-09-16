# coding: utf-8

from setuptools import find_packages, setup

from imgtoch import AUTHOR, EMAIL, NAME, VERSION, WEBSITE

description = "一个帮你将图片转为字符图片的模块。"
try:
    with open("README.md", "r", encoding="utf-8") as mdfile:
        long_description = mdfile.read()
except Exception:
    long_description = description

setup(
    name=NAME,
    version=VERSION,
    author=AUTHOR,
    author_email=EMAIL,
    maintainer=AUTHOR,
    maintainer_email=EMAIL,
    url=WEBSITE,
    description=description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT License",
    packages=find_packages(),
    install_requires=["Pillow"],
    python_requires=">=3.7",
    classifiers=[
        "Intended Audience :: Developers",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    keywords=["character picture", "character image", "picture", "image"],
)
