#!/usr/bin/env python3.8
import io
from setuptools import setup, find_packages


setup(
    name='dynamodb-stream-router',
    version='0.0.5',
    description='A framework for content-based routing of records in a Dynamodb Stream to the callable that should handle them',
    author='Mathew Moon',
    author_email='mmoon@quinovas.com',
    url='https://github.com/QuiNovas/dynamodb-stream-router',
    license='Apache 2.0',
    long_description=io.open('README.rst', encoding='utf-8').read(),
    long_description_content_type='text/x-rst',
    packages=find_packages(),
    package_dir={"dynamodb_stream_router": "dynamodb_stream_router"},
    install_requires=["sly", "simplejson", "typeguard"],
    scripts=[],
    python_requires=">=3.8",
    include_package_data=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.8',
    ],
)
