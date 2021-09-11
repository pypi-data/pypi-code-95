import pathlib
from setuptools import setup, find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(
    name="django-connect-mongo",
    version="1.1.0",
    description="we use this package to work with mongodb easier",
    long_description=README,
    long_description_content_type="text/markdown",
    # url="",
    author="hieucao192",
    author_email="hieucaohd@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
    ],
    packages=find_packages(),
    include_package_data=True,
    install_requires=["pymongo[srv]", "urllib", "copy", "datetime", "multiprocessing", "threading", "queue"],
)