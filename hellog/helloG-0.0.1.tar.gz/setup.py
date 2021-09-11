from setuptools import setup

with open("README.md", "r") as fh:
	long_description = fh.read()

setup(
	name='helloG',
	version='0.0.1',
	description='Say Hello G!',
	py_modules=["helloG"],
	package_dir={'': 'src'},
	classifiers=[
		"Programming Language :: Python :: 3",
		"Operating System :: OS Independent",
	],
	long_description=long_description,
	long_description_content_type="text/markdown",
	install_requires=[
		"blessings ~= 1.7",
	],
	extras_requires={
		"dev": [
			"pytest>=3.7",
		]
	},
	author="Quoc Anh",
	author_email="zone2120vn@gmail.com",
)