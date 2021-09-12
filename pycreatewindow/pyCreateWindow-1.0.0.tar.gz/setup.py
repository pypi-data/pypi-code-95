from setuptools import setup, find_packages
import codecs
import os

VERSION = '1.0.0'
DESCRIPTION = 'pyCreateWindow - SujithSouryaYedida'
LONG_DESCRIPTION = 'pyCreateWindow - is used to make a standalone apps from websites urls\n' \
                   'pyCreateWindow.info() - this is to know more information regarding the package\n' \
                   'pyCreateWindow.manual() - this is to get the manuel , or a guide book to use this package\n' \
                   'pyCreateWindow.create_window(x , y) - this is to create a window || So for that you need to use the following command : pyCreateWindow.create_window("url","name of the site")\n' \
                   'Package developer / Author : SujithSouryaYedida'

# Setting up
setup(
    name="pyCreateWindow",
    version=VERSION,
    author="SujithSouryaYedida",
    author_email="sujithsourya.yedida@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=['pyQt5','pyfiglet','colorama','pyQtWebEngine'],
    keywords=['python', 'py', 'yedida', 'python tutorial', 'SujithSouryaYedida','create','window','create window','pyCreateWindow'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)