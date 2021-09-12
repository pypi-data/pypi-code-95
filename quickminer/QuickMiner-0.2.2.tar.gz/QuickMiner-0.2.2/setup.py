from setuptools import setup, find_packages

VERSION = '0.2.2' 
DESCRIPTION = 'QuickMiner'
LONG_DESCRIPTION = 'Advanced test and simulated mining module'

setup(
        name="QuickMiner", 
        version=VERSION,
        author="Jason Odd",
        author_email="<jasonodd@gmaiI.com>",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=[], 
        
        keywords=['python', 'first package'],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Education",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
        ]
)