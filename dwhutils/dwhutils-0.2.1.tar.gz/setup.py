from pygments.lexer import include
from setuptools import setup, find_packages

setup(
    name='dwhutils',
    version='0.2.1',
    description='get utils for bitemporal data warehousing with mariadb',
    author='PoeticDrunkenCat',
    author_email='poeticdrunkencat@gmail.com',
    packages=find_packages(include=['dwhutils']),
    include_package_data=True,
    install_requires=[
        'dotenv',
        'sqlalchemy',
        'pandas',
        'pandas',
        'yaml',
        'pykeepass',
        'sshtunnel',
        'numpy',
        'termcolor2',
        'docker',
        'pymongo',
    ],
)
