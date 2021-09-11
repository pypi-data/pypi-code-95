from setuptools import setup, find_packages
import codecs
import os

VERSION = '0.0.1'
DESCRIPTION = 'HappySearch'
LONG_DESCRIPTION = 'This is a package used to make searches by giving them the url' \
                   'We need to simply need to install this package and simply say' \
                   'print(pySearch.search("give a url"))' \
                   'Then you can run the code and can see the website.' \
                   '' \
                   'Developed by Sujith Sourya Yedida'

# Setting up
setup(
    name="HappySearch",
    version=VERSION,
    author="SujithSouryaYedida",
    author_email="sujithsourya.yedida@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[],
    keywords=['pySearch', 'py', 'search', 'python tutorial', 'SujithSouryaYedida'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)