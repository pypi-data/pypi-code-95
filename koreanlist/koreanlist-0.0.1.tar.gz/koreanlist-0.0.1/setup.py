from setuptools import setup

from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='koreanlist',
    version='0.0.1',
    url='https://github.com/koreanbots/py-sdk',
    author='wonderlandpark',
    description='A mirror package for koreanbots.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=[],
    install_requires=['koreanbots'],
)
