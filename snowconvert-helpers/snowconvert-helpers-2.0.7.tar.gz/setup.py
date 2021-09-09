import codecs
import os
import setuptools
import re

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

HERE = os.path.abspath(os.path.dirname(__file__))

def read(*parts):
    # intentionally *not* adding an encoding option to open
    # see: https://github.com/pypa/virtualenv/issues/201#issuecomment-3145690
    return codecs.open(os.path.join(HERE, *parts), 'r').read()

def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

REQUIREMENTS = ['snowflake-connector-python>=2.4.3,<3.0.0',
    'Deprecated>=1.2.12,<2.0.0']

TEST_REQUIREMENTS = ['Deprecated>=1.2.12,<2.0.0']

KEYWORDS = ['Mobilize',
            'Snowflake',
            'Teradata',
            'BTEQ',
            'FastLoad',
            'MultiLoad',
            'TPT',
            'TPump',
            'database',
            'cloud']

setuptools.setup(
    name="snowconvert-helpers",
    packages=['snowconvert'],
    version=find_version('snowconvert', '__init__.py'),
    license='Proprietary License (Copyright (C) Mobilize.Net - All Rights Reserved)',
    description='Migration helpers for Mobilize SnowConvert for Teradata.',
    author='Mobilize.Net',
    author_email='info@mobilize.com',
    keywords=KEYWORDS,
    install_requires=REQUIREMENTS,
    tests_require=TEST_REQUIREMENTS,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://docs.mobilize.net/snowconvert/for-teradata/introduction",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: SQL",
        "Topic :: Database",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    python_requires='>=3.6',
)