from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

NAME = 'framed_title'
VERSION = '0.0.3'
INSTALL_REQUIRES = ['yatts>=1.0.0']
DESCRIPTION = 'Prints a framed title'
LONG_DESCRIPTION_CONTENT_TYPE = 'text/markdown'
KEYWORDS = ['python', 'text', 'frame', 'title', 'terminal', 'console']
CLASSIFIERS = [
    "Intended Audience :: Developers",
    "Programming Language :: Python :: 3.9",
    "Operating System :: OS Independent",
]

PY_MODULES = ['framed_title']
PACKAGE_DIR = {'': 'src'}

AUTHOR = 'xelorabb'
EMAIL = 'xelorabb@gmail.com'
URL = 'https://github.com/xelorabb/framed_title'
LICENSE = 'MIT'

# Setting up
setup(
    name=NAME,
    version=VERSION,
    author=AUTHOR,
    author_email=EMAIL,
    url=URL,
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type=LONG_DESCRIPTION_CONTENT_TYPE,
    install_requires=INSTALL_REQUIRES,
    keywords=KEYWORDS,
    classifiers=CLASSIFIERS,
    py_modules=PY_MODULES,
    package_dir=PACKAGE_DIR,
    license=LICENSE
)
