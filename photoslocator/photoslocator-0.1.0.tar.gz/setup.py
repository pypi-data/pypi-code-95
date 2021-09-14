from setuptools import setup, find_packages

with open('README.md') as file:
	readme_file = file.read()

setup(
	name='photoslocator',
	version='0.1.0',
	description='A simple tool to rename your photos using gps metadata',
	long_description=readme_file,
	long_description_content_type='text/markdown',
	author='Daniele Rossi',
	author_email='daniele.rossi27@unibo.it',
	url='https://github.com/DendoD96/photos_locator',
	keywords=['photography', 'gps-location'],
	license='GPLv3',
	scripts=["sample/photoslocator"],
	install_requires=[
		'Pillow',
		'geopy',
		'Unidecode'
	],
	packages=find_packages(exclude=['*.tests', '*.tests.*', 'tests.*', 'tests']),
	classifiers=[
		'Development Status :: 3 - Alpha',
		'Environment :: Console',
		'Intended Audience :: End Users/Desktop',
		'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
		'Topic :: Utilities',
		'Programming Language :: Python :: 3',
		'Programming Language :: Python :: 3.6',
		'Programming Language :: Python :: 3.7',
		'Programming Language :: Python :: 3.8',
		'Programming Language :: Python :: 3.9',
	]
)
