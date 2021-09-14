from setuptools import setup, find_packages

VERSION = '0.0.6' 
DESCRIPTION = 'PubMed article data collector'

with open('README.md', 'r') as rm:
    LONG_DESCRIPTION = rm.read()
LONG_DESCRIPTION = 'PubMed article data collector is able to let you download the metadata of bioinformatic acticle from the PubMed repository.'

# Setting up
setup(
        name="datacollector", 
        version=VERSION,
        author="Kwok Sun Cheng",
        author_email="<kwoksuncheng@unomaha.edu>",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=['beautifulsoup4', 'metapub', ], 
        keywords=['python', 'PubMed', 'Data collector'],
        classifiers= [
            "Intended Audience :: Education",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
        ]
)