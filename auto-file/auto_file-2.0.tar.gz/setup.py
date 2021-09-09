import setuptools
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setuptools.setup(
  name='auto_file',
  version='2.0',
  description='a module that can make all required folder and files for making python library and also genrate files for normal use',
  long_description=open('README.md').read(),
  url='https://github.com/Tech-with-anmol/pdftotexthttps://github.com/Tech-with-anmol/auto-file',  
  author='Anmol.py',
  author_email='anmollklfh@gmail.com',
  license='MIT',
  classifiers=classifiers,
  keywords='file', 
  packages=setuptools.find_packages(),
  install_requires=[],
) 