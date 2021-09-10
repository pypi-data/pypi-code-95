from setuptools import setup, find_packages
from os.path import join, dirname

setup(
    name='collect_pack',
    version='1.3',
    packages=find_packages(),
    long_description=open(join(dirname(__file__), 'README.md')).read(),
    author="Anybody and No one",
    install_requires=[
          'markdown',
          'argparse'
      ]
)
