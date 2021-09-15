import platform
import os.path as op
import os
import subprocess
import shutil

from setuptools import setup, find_packages

from distutils.command.build_py import build_py
from distutils.cmd import Command

descr = """Python package for human activity recognition"""

DISTNAME = 'pywear'
DESCRIPTION = descr
MAINTAINER = 'Actigraph LLC'
MAINTAINER_EMAIL = 'sheraz@khansheraz.com'
URL = ''
LICENSE = 'BSD (3-clause)'
DOWNLOAD_URL = ''
version = '0.0.1'

if __name__ == "__main__":
    setup(name=DISTNAME,
          maintainer=MAINTAINER,
          maintainer_email=MAINTAINER_EMAIL,
          description=DESCRIPTION,
          license=LICENSE,
          url=URL,
          version=version,
          download_url=DOWNLOAD_URL,
          long_description=open('README.rst').read(),
          classifiers=[
              'Intended Audience :: Science/Research',
              'Intended Audience :: Developers',
              'License :: OSI Approved',
              'Programming Language :: Python',
              'Topic :: Software Development',
              'Topic :: Scientific/Engineering',
              'Operating System :: Microsoft :: Windows',
              'Operating System :: POSIX',
              'Operating System :: Unix',
              'Operating System :: MacOS',
          ],
          platforms='any',
          install_requires=[
              'pandas'
          ],
          packages=find_packages()
          )
