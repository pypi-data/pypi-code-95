from setuptools import setup, find_packages
setup(
	name='ddgun',
	version='0.0.2',
	packages=find_packages(),
	package_data={
		'ddgun': ['data/*'],
	},
	install_requires=[
		'Click',
		'pandas',
		'biopython',
	],
	python_requires='>=3.6',
	entry_points={
		'console_scripts': [
			'ddgun = ddgun.cli:cli',
		],
	},
)
