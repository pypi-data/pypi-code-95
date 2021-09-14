from setuptools import setup, find_packages

VERSION = '0.0.1' 
DESCRIPTION = 'Basic example of a Python package'
LONG_DESCRIPTION = 'A slightly longer description. Not at all cheeky or anything.'

# Setting up
setup(
       # the name must match the folder name 
        name="basic_example", 
        version=VERSION,
        author="Connor Drooff",
        author_email="<drooff452@gmail.com>",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=[], # add any additional packages that 
        
        keywords=['python', 'example package'],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Education",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
        ]
)

