import pathlib
from setuptools import setup, find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="cmc_csci046_sdasari8_containers",
    version="1.0.0",
    description="Tests and implements various recursive data structures such as binary trees, binary search trees, AVL trees, and heaps as well as other miscellaneous projects.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/shreyad8/new-containers",
    author="Shreya Dasari",
    author_email="sdasari5090@scrippscollege.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=find_packages(exclude=("tests",)),
    include_package_data=True,
)
