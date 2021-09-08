from setuptools import setup, find_packages
import codecs
import os

VERSION = '0.0.1'
DESCRIPTION = 'A basic hello package'

# Setting up
setup(
      name="pkg_try_19_mb",
      version=VERSION,
      author="Mehri",
      author_email="mehri.baniasadi92@gmail.com",
      description=DESCRIPTION,
      long_description_content_type="text/markdown",
      packages=find_packages(),
      install_requires=[
                        "numpy==1.17.4",
                        "nibabel==2.5.1",
                        "scipy==1.3.1",
                        "nnunet-inference-on-cpu-and-gpu==1.6.6",
                        "batchgenerators==0.21"],
      entry_points={
      'console_scripts': [
                          "preprocess = pkg_try_19_mb.preprocess:main",
                          ] },
      keywords=['python'],
      classifiers=[
                   "Development Status :: 1 - Planning",
                   "Intended Audience :: Developers",
                   "Programming Language :: Python :: 3",
                   "Operating System :: Unix",
                   "Operating System :: MacOS :: MacOS X",
                   "Operating System :: Microsoft :: Windows",
                   ]
      )
