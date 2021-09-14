from setuptools import setup, find_packages

setup(
  name = 'delft_physics_lab',
  packages = find_packages(),
  version = '0.4',
  license='MIT',
  description = 'delft physics lab',
  install_requires=[
    'numpy',
    'scipy',
    'matplotlib'
  ],
)