from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='PESearch',
  version='0.0.4',
  description='Abstractions for parsing questions.',
  long_description='Abstractions for parsing questions.',
  url='',  
  author='404PSI',
  author_email='reallytovald@gmail.com',
  license='MIT', 
  classifiers=classifiers,
  keywords='parser', 
  packages=find_packages(),
  install_requires=[''] 
)