from setuptools import setup, find_packages
import codecs
import os

VERSION = '1.0.0'
DESCRIPTION = 'pyGlobServe'
LONG_DESCRIPTION = 'A package which creates a server or a room to make TCP chat rooms or any hosted apps'

# Setting up
setup(
    name="pyGlobServe",
    version=VERSION,
    author="SujithSouryaYedida",
    author_email="sujithsourya.yedida@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=['pyfiglet','tqdm','colorama'],
    keywords=['server', 'python', 'tcp room', 'chat', 'SujithSouryaYedida','py','chat room','localhost','hosted','server room'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)