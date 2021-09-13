from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))
with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.8.1'
DESCRIPTION = 'A python package that fetches your public project(repos) details from github'

# Setting up
setup(
    name="gpfetcher",
    version=VERSION,
    author="Gautam Chandra Saha",
    author_email="devgautam1231@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=['bs4', 'requests', 'tqdm', 'lxml'],
    keywords=['python', 'github', 'projects',
              'repositories', 'JSON', 'scraper'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
