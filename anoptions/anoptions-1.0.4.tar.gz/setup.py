import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="anoptions",
    version="1.0.4",
    author="anttin",
    author_email="muut.py@antion.fi",
    description="Module to assist in defining application options and collecting user input for them from command line and environment variables.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/anttin/anoptions",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
