import setuptools

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setuptools.setup(
    name='microt_compliance',
    version="0.0.23",
    description='A package that transform intermediate log files into features of interest for analysis',
    url='https://bitbucket.org/mhealthresearchgroup/microt_compliance/src/master/',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Jixin Li, Aditya Ponnada',
    author_email='li.jix@northeastern.edu',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(),
    python_requires='>=3.7'
)