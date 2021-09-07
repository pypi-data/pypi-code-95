# Always prefer setuptools over distutils
from setuptools import setup, find_packages
from os import path
from io import open

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# read in requirements 
requirements = open('requirements.txt').readlines()
requirements = [r.strip() for r in requirements]

setup(
  name = 'neuralsampler',
  packages = find_packages(),
  version = '0.0.10',
  license='MIT',
  description = 'neural sampler',
  long_description=long_description,  # Optional
  long_description_content_type='text/markdown',
  author = 'Jimmy',
  author_email = 'jiahaoyao.math@gmail.com',
  url = 'https://github.com/JiahaoYao/neuralsampler',
  keywords = [
    'artificial intelligence',
    'generative models',
    'transformers',
  ],
  install_requires=requirements,  # Optional
  classifiers=[
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'Topic :: Scientific/Engineering :: Artificial Intelligence',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.6',
  ],
)
