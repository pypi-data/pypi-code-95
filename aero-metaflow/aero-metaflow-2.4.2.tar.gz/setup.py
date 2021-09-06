from setuptools import setup, find_packages

version = '2.4.2'

setup(name='aero-metaflow',
  version=version,
  description='Aero fork of Metaflow',
  author='Aero',
  author_email='aero@robbiea.co.uk',
  license='Apache License 2.0',
  packages=find_packages(exclude=['metaflow_test']),
  py_modules=['metaflow', ],
  install_requires = [
    'click>=7.0',
    'requests',
    'boto3',
    'pylint<2.5.0',
  ],
  tests_require = [
    'coverage'
  ],
  entry_points={
      'console_scripts': [
          'aero-core = metaflow.main_cli:cli',
      ],
  }
)
