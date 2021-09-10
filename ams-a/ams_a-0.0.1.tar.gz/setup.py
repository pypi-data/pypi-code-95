from setuptools import setup

with open('README.md', 'r') as fh:
    long_description = fh.read()

setup(
     classifiers=[
         "Programming Language :: Python :: 3",
         "Programming Language :: Python :: 3.6",
         "Programming Language :: Python :: 3.7",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
       ],
    name = 'ams_a',
    version = '0.0.1',
    description = 'hello!',
    py_modules = ['hello'],
    package_dir = {'': 'src'},

     long_description = long_description,
    long_description_content_type = 'text/markdown',
     
     
)
