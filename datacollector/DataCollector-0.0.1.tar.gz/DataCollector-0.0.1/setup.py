from setuptools import setup, find_packages

VERSION = '0.0.1' 
DESCRIPTION = 'PubMed article data collector'
LONG_DESCRIPTION = 'PubMed article data collector is able to let you download the metadata of bioinformatic acticle from the PubMed repository.'

# Setting up
setup(
       # the name must match the folder name 'verysimplemodule'
        name="DataCollector", 
        version=VERSION,
        author="Kwok Sun Cheng",
        author_email="<kwoksuncheng@unomaha.edu>",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=['beautifulsoup4', 'metapub'], # add any additional packages that 
        # needs to be installed along with your package. Eg: 'caer'
        
        keywords=['python', 'PubMed', 'Data collector'],
        classifiers= [
            "Intended Audience :: Education",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            # "Operating System :: Microsoft :: Windows",
        ]
)