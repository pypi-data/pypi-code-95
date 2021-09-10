import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="bitgrit-cloud-api",
    version="0.0.4",
    author="bitgrit inc",
    author_email="develop@bitgrit.net",
    description="Library to interact with our cloud service",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bitgrit-official/bitgrit-cloud",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
