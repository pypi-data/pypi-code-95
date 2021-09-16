import setuptools
with open(r'C:\Users\marple_tech\Desktop\Projects\telecoin\README.md', 'r', encoding='utf-8') as fh:
	long_description = fh.read()

setuptools.setup(
	name='telecoin',
	version='0.0.1',
	author='marple_tech',
	author_email='marple.te@yandex.ru',
	description='Simple library to make payments via telegram exchangers',
	long_description=long_description,
	long_description_content_type='text/markdown',
	url='https://github.com/marple-git/telecoin',
	packages=['telecoin'],
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
	python_requires='>=3.6',
)