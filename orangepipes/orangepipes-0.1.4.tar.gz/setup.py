from setuptools import find_packages, setup

setup(
	name='orangepipes',
	packages=find_packages(include=['orangepipes']),
	version='0.1.4',
	description='Python library to read an orange.yml file and write the variables to the system.',
	long_description=open('README.md').read(),
	long_description_content_type = 'text/markdown',
	url='',
	license='MIT',
	install_requires=['pyyaml==5.4.1']
)