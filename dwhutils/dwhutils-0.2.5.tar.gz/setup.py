from pygments.lexer import include
from setuptools import setup, find_packages

setup(
    name='dwhutils',
    version='0.2.5',
    description='get utils for bitemporal data warehousing with mariadb',
    author='PoeticDrunkenCat',
    author_email='poeticdrunkencat@gmail.com',
    packages=find_packages(include=['dwhutils']),
    include_package_data=True,
    install_requires=[
        'python-dotenv',
        'sqlalchemy',
        'pandas',
        'pyyaml',
        'pykeepass',
        'sshtunnel',
        'numpy',
        'termcolor2',
        'docker',
        'pymongo',
    ],
)
