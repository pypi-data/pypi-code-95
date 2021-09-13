from setuptools import setup, find_packages
import codecs
import os

# read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

VERSION = '0.2.5'
DESCRIPTION = 'Dbar Algorithm for EIT'


setup(
    name="py_dbar",
    version=VERSION,
    author="NablaIp",
    author_email = "<ivanpombo.eigen@gmail.com>",
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type = "text/markdown",
    packages = find_packages(),
    install_requires = ["numpy", "scipy", "pyamg", "pyeit", "matplotlib" ],
    keywords=['python', 'EIT', 'DBar Algorithm'],
    classifiers=[
       'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
    ]

)
