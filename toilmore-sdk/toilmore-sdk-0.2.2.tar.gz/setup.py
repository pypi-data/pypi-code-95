from setuptools import setup, find_packages

import os

# Getting the version from the right and only one place it is defined
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))


def _p(path):
    return _project_path(path)


def _project_path(path):
    return os.path.join(PROJECT_ROOT, path)


__pypi_packagename__ = "toilmore-sdk"

LICENSE_FILE = os.path.join(PROJECT_ROOT, 'LICENSE')
README_FILE = os.path.join(PROJECT_ROOT, "README.md")

url = 'https://pixellena.com/'

version = {}
with open(os.path.join(PROJECT_ROOT, "toilmoresdk/version.py")) as fp:
    exec(fp.read(), version)
version = version["__version__"]

with open(README_FILE, encoding='utf-8') as f:
    long_description = f.read()

setup(
    name=__pypi_packagename__,
    version=version,
    author='ShimmerCat',
    author_email='ops@pixellena.com',
    packages=find_packages(),
    scripts=[],
    url=url,
    license='ISC License',
    description=(
        'The Toilmore API SDK provides Python APIs to optimize and process '
        'images.'
    ),
    long_description=long_description,
    long_description_content_type='text/markdown',
    package_data={
        'toilmoresdk': ['json_schemas/*', ],
    },
    include_package_data=True,
    install_requires=[
        'aiohttp==3.7.3',
        'aiohttp-retry==2.1',
        'asyncfile==1.0.0',
        'jsonschema==3.2.0',
        'mypy==0.790',
        'certifi==2020.12.5',
    ],
    entry_points={
        'console_scripts': [
            'toilmoresdk = toilmoresdk.entry_point:main',
        ],
    },
    classifiers=[
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    keywords=[
        'image-optimization',
        'image-processing',
        'sdk',
        'shimmercat',
        'pixellena',
        'tilemore',
        'python',
    ]
)
