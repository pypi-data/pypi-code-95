from setuptools import setup

with open('README.md', 'r') as f:
	long_description = f.read()

setup(
	name='helloworldbygov',
	version='0.0.1',
	description='Say hello!',
	long_description=long_description,
	long_description_content_type='text/markdown',
	url='https://github.com/governorbaloyi/helloworld',
	author='Governor Baloyi',
	author_email='governor.baloyi@gmail.com',
	install_requires=[], # list of specifiers
	py_modules=['helloworldbygov'],
	package_dir={'': 'src'},
	extras_require={
		'dev': [
			'pytest>=3.7',
			'twine'
		],
	},
	classifiers=[ # https://pypi.org/classifiers
		"Programming Language :: Python :: 3",
		"Programming Language :: Python :: 3.6",
		"Programming Language :: Python :: 3.7",
		"License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)",
		"Operating System :: OS Independent"
	],
)