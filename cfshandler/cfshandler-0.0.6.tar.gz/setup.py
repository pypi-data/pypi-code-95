from setuptools import setup, find_packages

VERSION = '0.0.6'
DESCRIPTION = 'CFService Handler'
LONG_DESCRIPTION = 'Easily interface with CFService'

# Setting up
setup(
    # the name must match the folder name 'verysimplemodule'
    name="cfshandler",
    url="https://github.com/boxpositron",
    version=VERSION,
    author="David Ibia",
    author_email="<david.ibia@boxmarshall.com>",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[
        'certifi==2020.12.5',
        'chardet==3.0.4',
        'idna==2.10',
        'mccabe == 0.6.1',
        'pycodestyle == 2.7.0',
        'pyflakes == 2.3.1',
        'requests == 2.24.0',
        'toml == 0.10.2',
        'typing-extensions == 3.10.0.0',
        'urllib3 == 1.25.11',
        'zipp == 3.4.1',

    ],  # add any additional packages that
    # needs to be installed along with your package. Eg: 'caer'

    keywords=['python', 'cfservice'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
