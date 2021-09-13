import setuptools
import os
import sys

# read the contents of README file as long description
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Dependency for windows (pywin32)
if sys.platform.startswith('win'):
    if sys.version_info[:2] >= (3, 7):
        pywin32 = 'pywin32 >= 224'
    else:
        pywin32 = 'pywin32'
    install_requires = [pywin32]

setuptools.setup(
  name = 'test.centrify.dmc',
  packages = ['dmc'],
  version = '0.3', 
  license='	apache-2.0',
  description = 'Library to retrieve an access token to Centrify PAS from an enrolled machine',
  long_description=long_description,
  long_description_content_type='text/markdown',
  author = 'k',
  author_email = '',
  url = 'https://github.com/centrify/dmc-python',
  download_url = '',
  keywords = ['Centrify', 'DMC', 'Windows', 'Linux', 'PAS'],
  install_requires=install_requires,
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: Apache Software License',
    'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Operating System :: Microsoft :: Windows',
    'Operating System :: POSIX :: Linux'
  ],
)