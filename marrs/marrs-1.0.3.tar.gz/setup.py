from setuptools import setup, find_packages

setup(
	name='marrs',
	version='1.0.3',
	author='Oran Gilboa',
	author_email='oran.gilboa1@gmail.com',
	package_dir={'': 'src'},
	packages=find_packages(where='src'),
	package_data={'marrs': ['data/bundle.js']},
	scripts=[],
	url='https://github.com/oran1248/marrs',
	download_url='https://github.com/oran1248/marrs/archive/refs/tags/1.0.3.tar.gz',
	license='GNU GPL v3',
	description='Python package for Android Java apps researchers, built on top of tools like frida and adb',
	long_description='Marrs is a Python package for Android Java apps researchers, built on top of tools like frida and adb. Using Marrs you can write Python code that modifies fields\' value, calls methods, creates instances, hooks methods and more.',
	install_requires=[
		'frida~=14.2.18',
		'androguard~=3.3.5',
		'lxml~=4.6.2',
		'requests~=2.26.0',
		'colorama~=0.4.3',
		'appdirs~=1.4.4',
		'setuptools~=41.2.0'
	]
)
