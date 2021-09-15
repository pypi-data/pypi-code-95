
import setuptools
import sys 
from setuptools.command.test import test as TestCommand

"""
class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to pytest")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)
"""

def readme():
	with open('README.md') as f:
		return f.read()

setuptools.setup(name='MihkelMagicElectrical',
	version='0.8.0',
	author='Mihkel Kaarel Raidal',
	author_email = 'm.k.raidal@gmail.com',
	description = 'Automated analysis of superconductor electrical data.',
	long_description_content_type='text/markdown',
	long_description=readme(),
	license = 'MIT',
	classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    url="https://github.com/mihkelKR/MihkelMagic_Electrical",
    packages=setuptools.find_packages(),
    python_requires='>=3.9',
    #extras_required={ "dev": ["pytest>=3.7",],   },
    #tests_require=['pytest'],
    #cmdclass = {'test': PyTest},
    install_requires=[
		'numpy>=1.21.1',
		'xlwt>=1.3.0',
		'pandas>=1.3.1',
		],


	)




