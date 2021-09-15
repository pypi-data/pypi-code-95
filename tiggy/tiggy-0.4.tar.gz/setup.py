from setuptools import setup, find_packages

setup(
  name = 'tiggy',
  packages = find_packages(),
  version = '0.4',
  license='GPL v3.0',
  description = 'tiggy',
  install_requires=[
    'numpy',
    'einops',
    'torch',
  ],
)