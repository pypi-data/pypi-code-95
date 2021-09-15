from setuptools import setup

with open('README.md', 'r') as f:
	long_description = f.read()

setup(
	name='mygpio',
	version='1.0.0',
	description='GPIO Library which extends GPIO functions',
	long_description=long_description,
	long_description_content_type='text/markdown',
	url='',
	author='Governor Baloyi',
	author_email='governor.baloyi@gmail.com',
	install_requires=["RPi.GPIO"], # list of specifiers
	py_modules=['mygpio'],
	package_dir={'': 'mygpio'},
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