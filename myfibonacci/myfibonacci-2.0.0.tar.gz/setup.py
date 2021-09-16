from setuptools import setup, find_packages
import pathlib

setup(
	name='myfibonacci',
	version='2.0.0',
	description='Just testing my fibonacci numbers',
	author='Richard Sharp',
	packages=find_packages(where='src'),
	python_requires='>=3.6, <4',
)