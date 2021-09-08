from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '1.0'
DESCRIPTION = 'Data2Insights package'
LONG_DESCRIPTION = 'Data2Insights of python packages can be used to integrate the data2insights services with your applications to enhance services with the data2insighs services.'

# Setting up
setup(
    name="data2Insights",
    version=VERSION,
    author="Deepika",
    author_email="<mekalabhagyadeepika@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=['requests'],
    keywords=['Data2Insights','services','Text','Vision','Batch'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)