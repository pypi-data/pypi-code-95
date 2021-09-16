from setuptools import setup, find_packages

classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='Caribe',
  version='0.0.1',
  description='Trinidad dialect to standard english',
  long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
  url='',  
  author='Keston Smith',
  author_email='keston.smith@my.uwi.edu',
  license='MIT', 
  classifiers=classifiers,
  keywords='converter', 
  packages=find_packages(),
  install_requires=[''] 
)