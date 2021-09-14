import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="hello_universe",
    version="0.0.4",
    author="M JAYANTH VARMA",
    author_email="jayanthvarma134@gmail.com",
    description="A rookie pypi package to print Hello Universe",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jayanthvarma134/hello-universe",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
) 