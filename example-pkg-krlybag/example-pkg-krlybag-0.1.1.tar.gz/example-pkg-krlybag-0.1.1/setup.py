import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
name = "example-pkg-krlybag",
version = "0.1.1",
author = "Karla A",
author_email = "krlybag@yahoo.com",
description = "A small example package",
long_description = long_description,
long_description_content_type = "text/markdown",
url = "https://github.com/pypa/sampleproject",
classifiers = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent"],

python_requires =" >=3.6",
)