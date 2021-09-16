import TPM2PPF_learntools
from setuptools import setup
from setuptools import find_packages

setup(name='TPM2PPF_learntools',
      version=TPM2PPF_learntools.__version__,
      description='Utilities for The TP of the PPF Master 2, adapted from Kaggle Learn exercises',
      url='http://github.com/antoinetavant/learntools',
      author='Antoine Tavant',
      author_email='antoine.tavant@polytechnique.edu',
      license='Apache 2.0',
      packages=find_packages(),
      zip_safe=True,
        install_requires=[
          'tqdm',
          'matplotlib',
          'numpy',
          'scipy'
      ],)
