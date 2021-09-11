import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="grep_func",
    version="1.0.1",
    packages=setuptools.find_packages(),
    description="A python package to grep 'functions' within modules",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/karry3775/grep_func",
    classifiers=(
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
