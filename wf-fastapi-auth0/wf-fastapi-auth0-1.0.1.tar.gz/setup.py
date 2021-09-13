import json
import os
from setuptools import setup, find_packages


BASEDIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(BASEDIR, "VERSION")) as fp:
    VERSION = fp.read()

print(VERSION)

BASE_DEPENDENCIES = [
    'requests',
    'fastapi',
    'auth0-python',
    'python-jose',
    'cachetools',
]

DEVELOPMENT_DEPENDENCIES = [
    'autopep8>=1.5',
    'pylint>=2.10.2',
]

# allow setup.py to be run from any path
os.chdir(os.path.normpath(BASEDIR))

setup(
    name='wf-fastapi-auth0',
    packages=find_packages(),
    version=VERSION,
    include_package_data=True,
    description='Library to simplify adding Auth0 support to FastAPI.',
    long_description='Will get to this someday',
    url='https://github.com/WildflowerSchools/wf-fastapi-auth0',
    author='Paul DeCoursey',
    author_email='paul.decoursey@wildflowerschools.org',
    install_requires=BASE_DEPENDENCIES,
    extras_require={
        'development': DEVELOPMENT_DEPENDENCIES
    },
    keywords=['auth', 'authentication', 'auth0', 'fastapi'],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
    ]
)
