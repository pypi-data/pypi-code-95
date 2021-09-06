from setuptools import setup
from setuptools import find_packages
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()


setup(
    name='el-compX-scraper', ## This will be the name your package will be published with
    version='0.1.5', 
    description='This package scrapes features of elements and compounds from specified websites',
    url='https://github.com/barmiy01/Webscraping_Project.git', # Add the URL of your github repo if published 
                                                                   # in GitHub
    author='Bilal Armiyawo', # Your name
    license='MIT',
    packages=find_packages(), # This one is important to explain. See the notebook for a detailed explanation
    install_requires=['requests', 'beautifulsoup4', 'selenium', 'pandas', 'sqlalchemy'], # For this project we are using two external libraries
                                                     # Make sure to include all external libraries in this argument

    long_description=long_description,
    long_description_content_type='text/markdown'

)
