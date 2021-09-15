from setuptools import setup

with open('README.md', 'r') as f:
	long_description = f.read()

setup(
	name='mygpio',
	version='0.0.2',
	description='GPIO Library which extends GPIO functions',
	long_description=long_description,
	long_description_content_type='text/markdown',
	url='',
	author='Governor Baloyi',
	author_email='governor.baloyi@gmail.com',
	install_requires=[], # list of specifiers
	py_modules=['mygpio'],
	package_dir={'': 'mygpio'},
	extras_require={
		"dev": [
			"pytest>=3.7",
		],
	},
	classifiers=[ 
		# https://pypi.org/classifiers
	],
)