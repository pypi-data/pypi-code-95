from setuptools import setup


install_requires = [
	'numpy',
	'tensorflow'
]

tests_require = [
	'pathlib'
]

setup(
	name = 'tf_livepatch_lr',
	version = '0.0.4',
	url = 'https://github.com/andrewerf/tf_livepatch_lr',
	author = 'Andrew Aralov',
	author_email = 'andrew-aralov@yandex.ru',
	packages = ['tf_livepatch_lr', 'tf_livepatch_lr.test'],
	license = 'LICENSE.txt',
	description = 'Simple project which allows you to change the learning rate schedule '
				  'without stopping the training process (tensorflow only)',
	long_description_content_type = 'text/markdown',
	long_description = open('README.md').read(),
	install_requires = install_requires,
	tests_require = tests_require,

	classifiers = [
		'Programming Language :: Python :: 3 :: Only',
		'License :: OSI Approved :: MIT License',
		'Intended Audience :: Developers'
	]
)
