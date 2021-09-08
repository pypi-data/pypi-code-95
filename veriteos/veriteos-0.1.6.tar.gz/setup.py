from setuptools import setup, find_packages

VERSION = '0.1.6'
DESCRIPTION = 'Veriteos sentinel events registry'

setup(
    name="veriteos",
    version=VERSION,
    author="Veriteos Dev Team",
    author_email="<admin@veriteos.com>",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=['marshmallow', 'requests'],
    keywords=['veriteos', 'veriteos client', 'veriteos events register'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',  
)