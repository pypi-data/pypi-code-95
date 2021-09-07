from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.md'), 'r', encoding='utf-8') as f:
    readme = f.read()

setup(
    name="cpntools4py",
    packages=find_packages(),
    version="1.2.0",
    license="MIT",
    install_requires=['SNAKES'],
    author='k208576',
    author_email='k208576@ie.u-ryukyu.ac.jp',
    url='https://gitlab.ie.u-ryukyu.ac.jp/k208576/cpntools4py',
    description='Support parsing of xml file which export color petri net from CPNTools',
    long_description=readme,
    long_description_content_type="text/markdown",
    classifiers=[
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: MIT License',
    ],
)