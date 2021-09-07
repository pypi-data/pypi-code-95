"""Setup module for Ionic Client SDK
"""

import os

# Always prefer setuptools over distutils, but fallback if needed.
usingSetupTools = True
try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup
    usingSetupTools = False

# To use a consistent encoding
from codecs import open
from os import path, environ

projectName = 'ionicsdk'

setup(
    name=projectName,

    version=open(os.path.join(projectName, 'VERSION')).read().strip(),

    description='Ionic Machina Client SDK',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",

    url='https://ionic.com/developers/',
    project_urls={
        'SDK Documentation': 'https://dev.ionic.com/sdk/docs/ionic_platform_sdk?language=python',
    },
    # Author details
    author='Ionic Security Inc.',
    author_email='dev@ionic.com',

    license='License Agreement for Ionic Resources',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers = [ #   3 - Alpha
                    #   4 - Beta
                    #   5 - Production/Stable
                    'Development Status :: 5 - Production/Stable',

                    # Indicate who your project is intended for
                    'Intended Audience :: Developers',
                    'Topic :: Software Development :: Libraries :: Python Modules',

                    # Pick your license option from the list at PyPi.org
                    'License :: Other/Proprietary License',

                    # Supported Python versions
                    'Programming Language :: Python',
                    'Programming Language :: Python :: 3',
                   
                    # Supported OS
                    'Operating System :: Microsoft :: Windows :: Windows 10',
                    'Operating System :: Microsoft :: Windows :: Windows 8.1',
                    'Operating System :: Microsoft :: Windows :: Windows 8',
                    'Operating System :: MacOS :: MacOS X',
                    'Operating System :: POSIX :: Linux',
                    ],

    # What does your project relate to?
    keywords='encryption user-authentication cryptography key-management data-security',

    packages=find_packages() if usingSetupTools else [projectName],

    package_data={projectName : ['*.*', '*/*.*', '*/*/*.*', '*/*/*/*.*']},

    include_package_data=True,
)
