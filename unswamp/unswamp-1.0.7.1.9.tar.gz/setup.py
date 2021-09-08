# https://github.com/pypa/sampleproject/blob/main/setup.py
from setuptools import setup, find_packages
from unswamp import __version__
version = __version__

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name="unswamp",
    version=version,
    author="Stefan Kaspar",
    author_email="me@fullbox.ch",
    description="A python package for data quality unit testing.",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://gitlab.com/debugair/unswamp",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Quality Assurance",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords="data, quality, test, unittest",
    python_requires=">=3.6",
    package_data={
            "": [
                    "templates/*.html",
                    "templates/*.js",
                ],
    },
    project_urls={
        'Bug Reports': 'https://gitlab.com/debugair/unswamp/-/issues',
        'Source': 'https://gitlab.com/debugair/unswamp',
    },
)
