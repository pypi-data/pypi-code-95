import os

import setuptools
from setuptools import setup

install_requires = [
    "numpy",
    "keras",
    "tokenizer_tools",
    "flask",
    "flask-cors",
    "ioflow",
    "tf-crf-layer",
    "tf-attention-layer",
    "tensorflow==1.15",
    "deliverable_model",
    "gunicorn",
    "micro_toolkit",
    "seq2annotation",
    "mtnlpmodel"
]


setup(
    # _PKG_NAME will be used in Makefile for dev release
    name=os.getenv("_PKG_NAME", "sem_reject"),
    version="0.1.4",
    packages=setuptools.find_packages(),
    include_package_data=True,
    url="https://github.com/xiaomihao/sem_reject",
    license="Apache 2.0",
    author="Xiao Mi",
    author_email="1922188869@qq.com",
    description="sem_reject",
    install_requires=install_requires,
)
