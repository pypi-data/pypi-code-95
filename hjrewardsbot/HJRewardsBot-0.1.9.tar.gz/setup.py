from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.1.9'
DESCRIPTION = 'Bing Rewards Bot by Hassan'
LONG_DESCRIPTION = 'A package that allows to complete bing bot rewards'

# Setting up
setup(
    name="HJRewardsBot",
    version=VERSION,
    author="Hassan jlilati",
    author_email="<hassanjlilati10000@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=['webdriver_manager', 'selenium', 'requests'],
    keywords=['python', 'rewards'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows",
    ]
)