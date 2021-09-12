from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='my_simple_split',
  version='0.0.1',
  description='A very basic splitter',
  long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
  url='',  
  author='Yaryk Dyhanov',
  author_email='duhanov2003@gmail.com',
  license='MIT', 
  classifiers=classifiers,
  keywords='split', 
  packages=find_packages(),
  install_requires=[''] 
)