from setuptools import setup, find_packages


def file(name: str) -> str:
	with open(name, 'r') as f:
		return f.read()


setup(
	name='blep',
	version='0.0.1',
	description='Static site generator.',
	long_description=file('README.md'),
	long_description_content_type='text/markdown',
	url='https://git.aphrodite.dev/Tools/blep',
	license='CNPLv6',
	author='Artemis',
	author_email='git@artemix.org',
	packages=find_packages(),
	install_requires=[
	],
	classifiers=[
		'Environment :: Console',
		'Operating System :: OS Independent',
		'Programming Language :: Python :: 3 :: Only',
		'Topic :: Internet',
		'Typing :: Typed',
	]
)
