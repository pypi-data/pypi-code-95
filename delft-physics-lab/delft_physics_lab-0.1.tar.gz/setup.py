from setuptools import setup, find_packages

setup(
  name = 'delft_physics_lab',
  packages = find_packages(),
  version = '0.1',
  license='MIT',
  description = 'delft physics lab',
  install_requires=[
    'numpy>=1.21',
    'scipy>=1.7.1',
    'matplotlib>=3.4.3'
  ],
)