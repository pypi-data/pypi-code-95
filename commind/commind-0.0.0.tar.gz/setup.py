from sys import platform
from setuptools import setup, find_packages

setup(
    name = "commind",
    version = "0.0.0",
    keywords = ["mindmap","mind","commandline"],
    description = "Generate mindmap with command line",
    license = "GPL v3.0 License",

    url = "https://github.com/zwhsh/PyComMind",
    author = "zwhsh",
    
    packages = find_packages(),
    include_package_data = True,
    platforms = "any",
    install_requires = [],
    
    scripts = [],
    entry_points = {
        'console_scripts': [
            'commind = commind:main'
        ]       
    }
)