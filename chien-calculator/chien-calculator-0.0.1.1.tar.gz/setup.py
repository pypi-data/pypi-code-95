from setuptools import setup
from os import path
import pathlib

############## Read long description from README.MD

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.MD'), encoding='utf-8') as f:
   long_description = f.read()

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.MD").read_text()

############# Setup package from source

setup(name='chien-calculator',
      version='0.0.1.1',
      description='Shows how to use setup.py',
      url='https://www.domain.com',
      author='Nguyen Hong Chien',
      license='GPLv3',
      packages=['calculator'],
      classifiers = [
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7'
      ],
      keywords='calculatortool',
      include_package_data=True,
      long_description=README,
      long_description_content_type='text/markdown'
)
