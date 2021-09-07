import setuptools
import os
import sys
 
with open("README.md", "r") as fh:
    long_description = fh.read()

# Dependency for windows
if sys.platform.startswith('win'):
    if sys.version_info[:2] >= (3, 7):
        pywin32 = 'pywin32 >= 224'
    else:
        pywin32 = 'pywin32'
    install_requires = [pywin32]

setuptools.setup(
    name="test.centrify.dmc", 
    version="0.0.1",
    author="Andrew Schilling",
    author_email="andrew.schilling@centrify.com",
    description="Proposed fix to Centrify's centrify.dmc module so Windows is supported",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=['dmc'],    
    install_requires=install_requires,
    python_requires='>=3.6',
)