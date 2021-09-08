from setuptools import setup

setup(name='torrequest-reborn',
  version='0.0.1',
  description='A simple interface for HTTP(s) requests over Tor',
  url='http://github.com/scuty2000/torrequest-reborn',
  author='Luca Scutigliani',
  author_email='lucascutigliani2@gmail.com',
  license='MIT',
  py_modules=['torrequest-reborn'],
  install_requires=[
    'PySocks>=1.5.7',
    'requests>=2.11.0',
    'stem>=1.4.0'
  ],
  zip_safe=False)

