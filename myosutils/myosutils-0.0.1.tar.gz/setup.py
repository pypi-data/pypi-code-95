from setuptools import setup

with open('README.md', 'r') as f:
	long_description = f.read()

setup(
	name='myosutils',
	version='0.0.1',
	description='OS Utils Library',
	long_description=long_description,
	long_description_content_type='text/markdown',
	url='https://github.com/governorbaloyi/pypi-myosutils',
	author='Governor Baloyi',
	author_email='governor.baloyi@gmail.com',
	install_requires=['contextlib', 'os', 'termios'], # list of specifiers
	py_modules=['myosutils'],
	package_dir={'': 'myosutils'},
	extras_require={
		"dev": [
			"pytest>=3.7",
		],
	},
	classifiers=[ 
		'Development Status :: 1 - Planning',
		'Framework :: Pytest',
		'License :: OSI Approved :: MIT License',
		'Programming Language :: Python :: 3 :: Only',
	],
)