from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

VERSION = '0.5'
DESCRIPTION = 'DeriveHelper Script'

# Setting up
setup(
    name="derivehelper",
    version=VERSION,
    author="m-benja",
    author_email="<m.benja@protonmail.ch>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires = ['argon2_cffi', 'cryptography', 'bcrypt', 'pynacl', 'passlib'],
    keywords=['python', 'cryptography'],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)