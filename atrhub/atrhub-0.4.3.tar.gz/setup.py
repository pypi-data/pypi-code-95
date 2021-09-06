# -*- coding: utf-8 -*-
import io
import re
from setuptools import setup, find_packages

with io.open('atrhub/__init__.py', 'rt', encoding='utf8') as f:
    version = re.search(r'__version__ = \'(.*?)\'', f.read()).group(1)

with open('requirements.txt', 'r') as f:
    INSTALL_REQUIRES = f.readlines()

try:
    with open('requirements-dev.txt', 'r') as f:
        TESTS_REQUIRE = f.readlines()
        TESTS_REQUIRE.remove("-r requirements.txt")
except:
        TESTS_REQUIRE = None

try:
    with open("README.md", "r") as readmefile:
        long_description = readmefile.read()
except:
        long_description = None

setup(
    name='atrhub',
    description='ATR xml files handler',
    long_description=long_description,
    long_description_content_type="text/markdown",
    version=version,
    url='https://www.gisce.net',
    author='Xavi Torelló',
    author_email='devel@gisce.net',
    packages=find_packages(),
    install_requires=INSTALL_REQUIRES,
    tests_require=TESTS_REQUIRE,
    license='General Public Licence 3',
    provides=['atrhub'],
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7"
    ],
    entry_points="""
        [console_scripts]
        atrhub=atrhub.cli:main
    """,

)
