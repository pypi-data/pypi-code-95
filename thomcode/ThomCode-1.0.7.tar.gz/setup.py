from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='ThomCode',
  version='1.0.7',
  description='Solution to all your problems',
  long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
  url='',  
  author='Thom van Hamburg',
  author_email='Thomniville@gmail.com',
  license='MIT', 
  classifiers=classifiers,
  keywords='ThomCode, pi, sqrt, factorial, prime, list, biominal coefficient, geometry, matrix, fibonacci sequence, game', 
  packages=find_packages(),
  install_requires=[''] 
)